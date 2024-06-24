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
				
	def init(self: Self, session: AbstractSession | NoneType = None):
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
		
	def canDeleteUser(self: Self, another: Self) -> bool:
		return self.model.role == sql.ProjectRole.admin
			
	def canJoinProject(self: Self, project: Project) -> bool:
		return not self.inProject(project) and self.model.role == sql.ProjectRole.worker
		
	def canEditProject(self: Self, project: Project | NoneType = None) -> bool:
		if not project:
			return self.model.role == sql.ProjectRole.manager
		else:
			return project.owner == self
			
	def canEditResource(self: Self, resource: Resource | NoneType = None) -> bool:
		if not resource:
			return self.model.role == sql.ProjectRole.manager
		else:
			return project.owner == self
		
	def canEditUser(self: Self, user: User | NoneType = None) -> bool:
		return self.model.role == sql.ProjectRole.admin
		
	def canEdit(self: Self, kind: str, item: Project | Resource | User | NoneType = None) -> bool:
		if kind == "project":
			return self.canEditProject(item)
		elif kind == "resource":
			return self.canEditResource(item)
		elif kind == "user":
			return self.canEditUser(item)
	
	def canView(self: Self, kind: str, wrap: User | Project | Resource) -> bool:
		if kind == "project":
			return self.model.role == sql.ProjectRole.admin or self.inProject(wrap)
		elif kind == "resource":
			role = self.model.role
			return role == sql.ProjectRole.admin or
				role == sql.ProjectRole.manager
		elif kind == "user":
			if wrap == self:
				return True
			role = self.model.role
			if role == sql.ProjectRole.admin:
				return True
			elif role == sql.ProjectRole.manager:
				return wrap.model.role == sql.ProjectRole.worker
			elif role == sql.ProjectRole.worker:
				return False
				
	def delete(self: Self) -> NoneType:
		self.deleteProjects()
		super().delete()
		
	def deleteProjects(self: Self) -> NoneType:
		project = self.project
		if project and self.owner(project):
			project.delete()
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.login
				
		elif attr == "manager":
			return User(self.model.manager_id)
				
		elif attr == "projects":
			with self.subsession as subsession:
				return [ Project(ide, self.session) for ide in subsession(Query(
					select(sql.ProjectsToResourcesLkp.project_id)
					.where(sql.ProjectsToResourcesLkp.user_id == self.id),
					True )) ]
					
		elif attr == "ownedProjects":
			with self.subsession as subsession:
				return [ Project(name, self.session) for name in subsession(Query(
					select(sql.Projects.name)
					.where(sql.Projects.owner_id == self.id),
					True )) ]
		
		return super().__getattr__(attr)
		
	def acceptVisitor(self: Self, visitor: Any, *,
		advanced: bool = False) -> Any:
		return visitor.visitUser(self, advanced = advanced)
	
	def delete(self: Self) -> NoneType:
		with self.subsession as subsession:
			rows = subsession(Query(
				select(sql.ProjectsToResourcesLkp)
				.where(sql.ProjectsToResourcesLkp.user_id == self.id), True))
			for row in rows:
				subsession.add(row, toDelete = True)
			for project in self.ownedProjects:
				project.delete()
		super().delete()
		
	def addProject(self: Self, project: "Project", allocation: float = 1.0) -> NoneType:
		with self.subsession as subsession:
			subsession.add(sql.ProjectsToResourcesLkp(project.id, self.id, None, allocation))
			
	def releaseProject(self: Self, project: "Project") -> NoneType:
		with self.subsession as subsession:
			row = subsession(Query(
				select(sql.ProjectsToResourcesLkp)
				.where(sql.ProjectsToResourcesLkp.project_id == project.id and
					sql.ProjectsToResourcesLkp .user_id == self.id)))
			subsession.add(row, toDelete = True)
			
	def inProject(self: Self, project: "Project") -> bool:
		with self.subsession as subsession:
			return subsession(Query(
				select(sql.ProjectsToResourcesLkp)
				.where((sql.ProjectsToResourcesLkp.project_id == project.id) &
					(sql.ProjectsToResourcesLkp.user_id == self.id)))) is not None 
			
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
				return [ User(ide, self.session) for ide in subsession(Query(
					select(sql.ProjectsToResourcesLkp.user_id)
					.where(sql.ProjectsToResourcesLkp.project_id == self.id),
					True )) if ide is not None ]
		
		elif attr == "resources":
			with self.subsession as subsession:
				return [ Resource(ide, self.session) for ide in subsession(Query(
					select(sql.ProjectsToResourcesLkp.resource_id)
					.where(sql.ProjectsToResourcesLkp.project_id == self.id),
					True )) if ide is not None ]
				
		elif attr == "owner":
			with self.subsession as subsession:
				return User(subsession(Query(
					select(sql.Projects.owner_id).where(sql.Projects.name == self.name)
					)))
				
		return super().__getattr__(attr)
		
	def delete(self: Self) -> NoneType:
		with self.subsession as subsession:
			rows = subsession(Query(
				select(sql.ProjectsToResourcesLkp)
				.where(sql.ProjectsToResourcesLkp.project_id == self.id), True))
			for row in rows:
				subsession.add(row, toDelete = True)
		super().delete()
		
	def acceptVisitor(self: Self, visitor: Any) -> Any:
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
		elif attr == "projects":
			with self.subsession as subsession:
				return [ Project(ide, self.session) for ide in subsession(Query(
					select(sql.ProjectsToResourcesLkp.project_id)
					.where(sql.ProjectsToResourcesLkp.resource_id == self.id),
					True )) ]
						
		return super().__getattr__(attr)
	
	def addProject(self: Self, project: Project, allocation: float = 1.0) -> NoneType:
		with self.subsession as subsession:
			subsession.add(sql.ProjectsToResourcesLkp(project.id, None, self.id, allocation))
			
	def releaseProject(self: Self, project: Project) -> NoneType:
		with self.subsession as subsession:
			row = subsession(Query(
				select(sql.ProjectsToResourcesLkp)
				.where((sql.ProjectsToResourcesLkp.project_id == project.id) &
					(sql.ProjectsToResourcesLkp.resource_id == self.id))))
			subsession.add(row, toDelete = True)
			
	def delete(self: Self) -> NoneType:
		with self.subsession as subsession:
			rows = subsession(Query(
				select(sql.ProjectsToResourcesLkp)
				.where(sql.ProjectsToResourcesLkp.resource_id == self.id), True))
			for row in rows:
				subsession.add(row, toDelete = True)
		super().delete()
			
	def acceptVisitor(self: Self, visitor: Any) -> Any:
		return visitor.visitResource(self)
	
	def inProject(self: Self, project: Project) -> bool:
		with self.subsession as subsession:
			return bool(subsession(Query(
				select(sql.ProjectsToResourcesLkp)
				.where((sql.ProjectsToResourcesLkp.project_id == project.id) &
					(sql.ProjectsToResourcesLkp.resource_id == self.id)))))
