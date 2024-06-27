import sqlModels as sql
from widgets import Label
from typing import Any, Self
from types import NoneType
from datetime import date, datetime

def nothing(arg):
	if arg is None:
		return True
	if arg == "":
		return True
	return False
	
class InputModel:
	
	def __new__(cls: type, args: list[Any], *, 
		password: str | NoneType = None, manager: str | NoneType = None) -> Self | NoneType:
		if any([ nothing(field) for field in args ]):
			return None
		if password == "":
			return None
		obj = super().__new__(cls)
		obj.init(*args, password = password, manager = manager)
		return obj

class Project(InputModel):

	def init(self: Self, name: str, description: str,
		start_date: date, end_date: date, status: str, *, password: NoneType = None,
		manager: NoneType = None) -> NoneType:
		self.name = name
		self.description = description
		self.start_date = start_date.date()
		self.end_date = end_date.date()
		self.status = status
		
	def sendTo(self: Self, sqlModel: sql.Projects) -> NoneType:
		sqlModel.name = self.name
		sqlModel.description = self.description
		sqlModel.start_date = self.start_date
		sqlModel.end_date = self.end_date
		sqlModel.status = self.status
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.name
		elif attr == "toSQL":
			return sql.Projects(name = self.name, description = self.description, 
				start_date = self.start_date, end_date = self.end_date,
				status = self.status, owner_id = self.owner_id)
		raise ValueError(self, attr)
	
	def __setattr__(self: Self, attr: str, value: Any) -> NoneType:
		if attr == "owner":
			self.owner_id = value.id
			return
		self.__dict__[attr] = value
		
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitProject(self)

class User(InputModel):

	def init(self: Self, login: str, name: str, surname: str, *,
		password: str | NoneType = None, manager: str | NoneType = None) -> NoneType:
		import wraps
		self.login = login
		self.name = name
		self.surname = surname
		self.role = sql.ProjectRole.worker if manager else sql.ProjectRole.manager
		self.manager_id = wraps.User(manager).id if manager else None
		self.password = password
		
	def sendTo(self: Self, sqlModel: sql.Users) -> NoneType:
		sqlModel.login = self.login
		sqlModel.name = self.name
		sqlModel.surname = self.surname
		sqlModel.role = self.role
		sqlModel.manager_id = self.manager_id
			
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitUser(self)
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.login
		elif attr == "toSQL":
			return sql.Users(login = self.login, name = self.name, 
				surname = self.surname, role = self.role, manager_id = self.manager_id,
				password = self.password, setup_time = datetime.now())
		raise ValueError(self, attr)
		
class Resource(InputModel):

	def init(self: Self, name: str, *, password: NoneType = None,
		manager: NoneType = None) -> NoneType:
		self.name = name
		
	def sendTo(self: Self, sqlModel: sql.TechnicalResources) -> NoneType:
		sqlModel.name = self.name
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.name
		elif attr == "toSQL":
			return sql.TechnicalResources(name = self.name)
		raise ValueError(self, attr)
		
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitResource(self)

