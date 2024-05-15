import sqlModels as sql
from widgets import Label
from typing import Any, Self
from types import NoneType
from datetime import date

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
		print("Teraz 2")
		obj = super().__new__(cls)
		print("Teraz 3")
		print(args)
		obj.init(old = old.value if old else None, *args)
		print("Teraz 4")
		return obj
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "notConsistent":
			return None
		else:
			raise AttributeError(attr)

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

	def init(self: Self, name: str, surname: str, role: str, *, old: NoneType = None) -> NoneType:
		self.name = name
		self.surname = surname
		self.role = role
		
	def sendTo(self: Self, sqlModel: sql.Users) -> NoneType:
		sqlModel.name = self.name
		sqlModel.surname = self.surname
		sqlModel.role = self.role
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "password":
			return None
		else:
			return super().__getattr__(attr)
			
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitUser(item)
		
class UserCredentials(InputModel):
			
	def init(self: Self, login: str, *, old: str | NoneType = None) -> NoneType:
		self.login = login
		if old:
			self.old = old
		
	def sendTo(self: Self, sqlModel: sql.Users) -> NoneType:
		sqlModel.login = self.login
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.login
		return super().__getattr__(attr)
		
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None)-> Any:
		return visitor.visitUser(self)

class FullUserCredentials(UserCredentials):

	def init(self: Self, login: str, password: str, repeated: str, *,
		old: str | NoneType = None) -> NoneType:
		print("password:", password)
		print("repeated:", repeated)
		print("Teraz 5")
		super().init(login, old = old)
		print("Teraz 6")
		self.password = password
		self.repeated = repeated
	
	def sendTo(self: Self, sqlModel: sql.Users) -> NoneType:
		super().sendTo(sqlModel)
		sqlModel.password = self.password
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "notConsistent":
			if self.password != self.repeated:
				return "passwords"
			else:
				return None
		return super().__getattr__(attr)
	
class User(InputModel):

	def init(self: Self, credentials: UserCredentials,
		description: UserDescription, *, old: NoneType = None) -> NoneType:
		self.credentials = credentials
		self.description = description
			
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.credentials.login
		elif attr == "toSQL":
			return sql.Users(login = self.credentials.login, password = self.credentials.password, 
				name = self.description.name, surname = self.description.surname,
				role = self.description.role)
		elif attr == "password":
			return self.credentials.password
		return super().__getattr__(attr)
			
	def __setattr__(self: Self, attr: str, value: Any) -> NoneType:
		if attr == "password":
			self.credentials.password = value
		else:
			self.__dict__[attr] = value
			
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitUser(self)
		
class Resource(InputModel):

	def init(self: Self, name: str, *, old: NoneType = None) -> NoneType:
		self.name = name
		
	def sendTo(self: Self, sqlModel: sql.Technical_Resources) -> NoneType:
		sqlModel.name = self.name
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.name
		elif attr == "toSQL":
			return sql.Technical_Resources(name = self.name)
		return super().__getattr__(attr)
		
	def acceptVisitor(self: Self, visitor: Any, item: str | NoneType = None) -> Any:
		return visitor.visitResource(self)
		
def makeUserCredentials(login: str | NoneType, password: str | NoneType,
	repeated: str | NoneType, *, old: OldPassword | NoneType = None,
	newRequired: bool = False) -> UserCredentials | NoneType:
		if nothing(password) and nothing(repeated) and not newRequired:
			return UserCredentials([login], old = old)
		else:
			print("Teraz")
			return FullUserCredentials([login, password, repeated],
				old = old)

	
def makeUser(logged, advanced, login, password,
	repeated, old, name, surname, role):
	if logged:
		if advanced:
			return makeUserCredentials(login, password, repeated,
				old = OldPassword(old))
		else:
			return UserDescription([name, surname, role])
	else:
		return User([makeUserCredentials(login, password, repeated, newRequired = True),
			UserDescription([name, surname, role])])

