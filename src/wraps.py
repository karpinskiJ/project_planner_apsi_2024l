from __future__ import annotations
from contextlib import closing
from session import *
import sqlModels as sql
import sqlmodel
from sqlmodel import select
import inputModels as inpute
from inputModels import InputModel
from typing import Any, Self
from types import NoneType
import elemental
import datetime

# This is the only file in which there are sql select and where

class General:

	def __new__(cls: type, item: str | int | InputModel | NoneType = None, 
		session: AbstractSession | NoneType = None) -> General | NoneType:
		if item is None and cls is not General:
			return None
		obj = super().__new__(cls)
		if cls is General:
			obj.init(session)
		else:
			obj.init(item, session)
		return obj
		
	@staticmethod
	def make(kind: str, item: str | int | InputModel) -> Self:
		if kind == "user":
			return User(item)
		elif kind == "project":
			return Project(item)
		elif kind == "resource":
			return Resource(item)
			
	def makeOfModel(self: Self, model: InputModel, item: str | NoneType = None) -> Self:
		return model.acceptVisitor(self, item)
		
	def visitUser(self: Self, model: inpute.UserCredentials | inpute.User) -> User:
		return User(model, self.session)
		
	def visitProject(self: Self, model: inpute.Project) -> Project:
		return Project(model, self.session)
	
	def visitResource(self: Self, model: inpute.Resource) -> Resource:
		return Resource(model, self.session)
		
	def nameOfId(self: Self, ide: int) -> str:
		kind = self.__class__.kind
		with self.subsession as subsession:
			return subsession(Query(
				select(elemental.uniqueNameField(kind))
				.where(elemental.modelType(kind).id == ide)
				))
				
	def init(self: Self, session: session.AbstractSession | NoneType = None):
		self.session = session
		
	def __ne__(self: Self, another: Self) -> bool:
		return not self == another	
				
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "id" or attr == "model":
			kind = self.__class__.kind
			model = elemental.modelType(kind)
			model = model if attr == "model" else model.id
			with self.subsession as subsession:
				return subsession(Query(
					select(model).where(elemental.uniqueNameField(kind) == self.uniqueName)
					))
		elif attr == "exists":
			return self.id is not None
		elif attr == "subsession":
			session = ProxySession(self, self.session) if self.session else Session(self)
			if not self.session:
				self.session = session
			return closing(session)
		else:
			raise AttributeError(attr, self.__class__)
			
	def edit(self: Self, model: InputModel, item: Self | NoneType = None) -> NoneType:
		old = None
		if item:
			old = item.model
			model.sendTo(old)
		with self.subsession as subsession:
			subsession.add(old if item else model.toSQL)
			
	def delete(self: Self) -> NoneType:
		with self.subsession as subsession:
			subsession.add(self.model, toDelete = True)
			
	def all(self: Self, kind: str) -> list[ sqlmodel.SQLModel ]:
		with self.subsession as subsession:
			return [ General.make(kind, item) for item in subsession(Query(
				select(elemental.uniqueNameField(kind)),
				True)) ]
				
	def empty(self: Self, kind: str) -> bool:
		return len(self.all(kind)) == 0

class User(General):
	
	kind = "user"
	
	def init(self: Self,
		ide: str | int | inpute.UserCredentials | inpute.User,
		session: AbstractSession | NoneType = None) -> NoneType:
		super().init(session)
		if type(ide) == str:
			self.login = ide
		elif type(ide) == int:
			self.login = self.nameOfId(ide)
		elif type(ide) == inpute.UserCredentials:
			self.login = ide.login
		elif type(ide) == inpute.User:
			self.login = ide.credentials.login
		else:
			raise ValueError(ide, self.__class__)
		
	def __eq__(self: Self, another: Self) -> bool:
		return another and self.login == another.login
	
	def makeAdmin(self: Self, parent: Self | NoneType = None) -> NoneType:
		if parent:
			parent = parent.id
		with self.subsession as subsession:
			subsession.add(sql.System_Admins(id = self.id, parent_id = parent,
				promotion_time = datetime.datetime.now()))
			
	def inherits(self: Self, another: Self) -> bool:
		anch = another.id
		sub = self.id
		with self.subsession as subsession:
			while sub is not None:
				sub = subsession(Query(
					select(sql.System_Admins.parent_id).where(sql.System_Admins.id == sub)
					))
				if sub == anch:
					return True
		return False
		
	def canDeleteUser(self: Self, another: Self) -> bool:
		return ( self == another or self.admin and 
			( not another.admin or another.inherits(self) ) )
	
	def owner(self: Self, project: Project) -> bool:
		with self.subsession as subsession:
			return (subsession(Query(
				select(sql.Projects.owner_id).where(sql.Projects.name == project.name)
				)) == self.id)
			
	def canJoinProject(self: Self, project: Project) -> bool:
		return self.project is None
		
	def canEditProject(self: Self, project: Project | NoneType = None) -> bool:
		if not project:
			return not self.project
		else:
			return self.admin or self.owner(project)
			
	def canEditResource(self: Self, resource: Resource | NoneType = None) -> bool:
		return self.admin
		
	def canEdit(self: Self, kind: str, item: Project | Resource | NoneType = None) -> bool:
		if kind == "project":
			return self.canEditProject(item)
		elif kind == "resource":
			return self.canEditResource(item)
			
	def delete(self: Self) -> NoneType:
		if self.admin:
			self.degrade()
		self.deleteProjects()
		super().delete()
		
	def deleteProjects(self: Self) -> NoneType:
		project = self.project
		if project and self.owner(project):
			project.delete()
				
	def degrade(self: Self) -> NoneType:
		parent = self.parent
		if not parent:
			first = self.firstChild
			if first:
				for child in self.children:
					if first != child:
						child.parent = first
				first.parent = None
			else:
				first = self.firstUser
				if first:
					first.makeAdmin(self)
					self.degrade()
					return
		else:
			for child in self.children:
				child.parent = parent
		with self.subsession as subsession:
			admin = subsession(Query(
				select(sql.System_Admins).where(sql.System_Admins.id == self.id)
				))
			subsession.add(admin, toDelete = True)
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.login
		elif attr == "admin":
			with self.subsession as subsession:
				return subsession(Query(
					select(sql.System_Admins.id).where(sql.System_Admins.id == self.id)
					)) is not None
	
		elif attr == "parent":
			if not self.admin:
				raise AttributeError(attr, self.__class__)
			with self.subsession as subsession:
				return User(subsession(Query(
					select(sql.System_Admins.parent_id).where(sql.System_Admins.id == self.id)
					)), self.session)
			
		elif attr == "children":
			if not self.admin:
				raise AttributeError(attr, self.__class__)
			with self.subsession as subsession:
				return [ User(ide, self.session) for ide in subsession(Query(
					select(sql.System_Admins.id).where(sql.System_Admins.parent_id == self.id),
					True )) ]
				
		elif attr == "firstChild":
			date = None
			firstChild = None
			for child in self.children:
				with self.subsession as subsession:
					result = subsession(Query(
						select(sql.System_Admins.id, sql.System_Admins.promotion_time)
						.where(sql.System_Admins.id == child.id)
						))
					if result:
						ide, newDate = result
				if date is None or newDate < date:
					date = newDate
					firstChild = ide
			if firstChild is not None:
				firstChild = User(firstChild)
			return firstChild
			
		elif attr == "firstUser":
			date = None
			firstUser = None
			for user in self.all("user"):
				with self.subsession as subsession:
					result = subsession(Query(
						select(sql.Users.id, sql.Users.setup_time)
						.where(sql.Users.id == user.id)
						))
					if result:
						ide, newDate = result
				if self != user and (date is None or newDate < date):
					date = newDate
					firstUser = ide
			if firstUser is not None:
				firstUser = User(firstUser)
			return firstUser
			
		elif attr == "position":
			if self.admin:
				if self.parent is None:
					return "head admin"
				else:
					return "admin"
			else:
				return "usual"
				
		elif attr == "project":
			with self.subsession as subsession:
				return Project(
					subsession(Query(
						select(sql.Users.project_id).where(sql.Users.login == self.login)
						)), self.session)
						
		elif attr == "owns":
			return self.project is not None and self.project.owner == self
		
		return super().__getattr__(attr)
	
	def __setattr__(self: Self, attr: str, value: Any) -> NoneType:
		if attr == "parent":
			with self.subsession as subsession:
				if not self.admin:
					raise AttributeError(attr, self.__class__)
				row = subsession(Query(
					select(sql.System_Admins).where(sql.System_Admins.id == self.id)
					))
				row.parent_id = value.id if value else None
				subsession.add(row)
				return
		elif attr == "project":
			value = None if (value is None) else value.id
			with self.subsession as subsession:
				row = subsession(Query(
					select(sql.Users).where(sql.Users.login == self.login)
					))
				row.project_id = value
				subsession.add(row)
				return	
		self.__dict__[attr] = value
		
	def acceptVisitor(self: Self, visitor: Any, *,
		advanced: bool = False) -> Any:
		return visitor.visitUser(self, advanced = advanced)
			
class Project(General):

	kind = "project"

	def init(self: Self, ide: str | int | inpute.Project,
		session: AbstractSession | NoneType = None) -> NoneType:
		super().init(session)
		if type(ide) == str:
			self.name = ide
		elif type(ide) == int:
			self.name = self.nameOfId(ide)
		elif type(ide) == inpute.Project:
			self.name = ide.name
		else:
			raise ValueError(ide, self.__class__)
			
	def __eq__(self: Self, another: Self) -> bool:
		return another and self.name == another.name
			
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.name
		elif attr == "users":
			with self.subsession as subsession:
				return [ User(login, self.session) for login in subsession(Query(
					select(sql.Users.login).where(sql.Users.project_id == self.id),
					True )) ]
		
		elif attr == "resources":
			with self.subsession as subsession:
				return [ Resource(name, self.session) for name in subsession(Query(
					select(sql.Technical_Resources.name)
					.where(sql.Technical_Resources.project_id == self.id),
					True )) ]
				
		elif attr == "owner":
			with self.subsession as subsession:
				return User(subsession(Query(
					select(sql.Projects.owner_id).where(sql.Projects.name == self.name)
					)))
				
		return super().__getattr__(attr)
		
	def delete(self: Self) -> NoneType:
		for user in self.users:
			user.project = None
		for resource in self.resources:
			resource.project = None
		super().delete()
		
	def acceptVisitor(self: Self, visitor: Any, *, advanced: bool = False) -> Any:
		return visitor.visitProject(self)

class Resource(General):

	kind = "resource"

	def init(self: Self, ide: str | int | inpute.Resource,
		session: AbstractSession | NoneType = None) -> NoneType:
		super().init(session)
		if type(ide) == str:
			self.name = ide
		elif type(ide) == int:
			self.name = self.nameOfId(ide)
		elif type(ide) == inpute.Resource:
			self.name = ide.name
		else:
			raise ValueError(ide, self.__class__)
			
	def __eq__(self: Self, another: Self) -> bool:
		return another and self.name == another.name
			
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.name
		elif attr == "project":
			with self.subsession as subsession:
				return Project(
					subsession(Query(
						select(sql.Technical_Resources.project_id)
						.where(sql.Technical_Resources.name == self.name)
						)), self.session)
						
		return super().__getattr__(attr)
						
	def __setattr__(self: Self, attr: str, value: Any) -> NoneType:
		if attr == "project":
			project_id = None if not value else value.id
			with self.subsession as subsession:
				row = subsession(Query(
					select(sql.Technical_Resources).where(sql.Technical_Resources.name == self.name)
					))
				row.project_id = project_id
				subsession.add(row)
			return
				
		self.__dict__[attr] = value
	
	def acceptVisitor(self: Self, visitor: Any, *, advanced: bool = False) -> Any:
		return visitor.visitResource(self)
		
