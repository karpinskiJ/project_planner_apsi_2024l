import sqlModels as sql
from widgets import Label
from typing import Any, Self
from types import NoneType
from datetime import date, datetime

class OldPassword:
	
	def __init__(self: Self, value: str | NoneType) -> NoneType:
		self.value = value

def nothing(arg):
	if arg is None:
		return True
	if arg == "":
		return True
	return False
	
class InputModel:
	
	def __new__(cls: type, args: list[Any], *, 
		old: OldPassword | NoneType = None)-> Self | NoneType:
		if any([ nothing(field) for field in args ]):
			return None
		if old and nothing(old.value):
			return None
		obj = super().__new__(cls)
		obj.init(old = old.value if old else None, *args)
		return obj
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "notConsistent":
			return None
		else:
			raise AttributeError(attr, self.__class__)

class Project(InputModel):

	def init(self: Self, name: str, description: str,
		start_date: date, end_date: date, status: str, *,old: NoneType = None) -> NoneType:
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
		return super().__getattr__(attr)
	
	def __setattr__(self: Self, attr: str, value: Any) -> NoneType:
		if attr == "owner":
			self.owner_id = value.id
			return
		self.__dict__[attr] = value
		
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitProject(self)

class UserDescription(InputModel):

	def init(self: Self, name: str, surname: str, role: str, *,
		password: str | NoneType = None) -> NoneType:
		self.name = name
		self.surname = surname
		self.role = role
		self.password = password
		
	def sendTo(self: Self, sqlModel: sql.Users) -> NoneType:
		sqlModel.name = self.name
		sqlModel.surname = self.surname
		sqlModel.role = self.role
			
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitUser(item)
		
class Resource(InputModel):

	def init(self: Self, name: str, *, old: NoneType = None) -> NoneType:
		self.name = name
		
	def sendTo(self: Self, sqlModel: sql.TechnicalResources) -> NoneType:
		sqlModel.name = self.name
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.name
		elif attr == "toSQL":
			return sql.TechnicalResources(name = self.name)
		return super().__getattr__(attr)
		
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitResource(self)

