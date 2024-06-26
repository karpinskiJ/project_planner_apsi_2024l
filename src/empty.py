from typing import Self, Any
from types import NoneType
from datetime import datetime

class Model:

	def __init__(self: Self) -> NoneType:
		self.model = self
	
	@staticmethod
	def make(kind: str) -> Self | NoneType:
		if kind == "project":
			return Project()
		elif kind == "resource":
			return Resource()
			
class User(Model):
	
	def __init__(self: Self) -> NoneType:
		super().__init__()
		self.login = ""
		self.password = ""
		self.repeatedPassword = ""
		self.name = ""
		self.surname = ""
		self.role = "" 

	def acceptVisitor(self: Self, visitor: Any) -> Any:
		return visitor.visitEmptyUser(self)
		
class Project(Model):
	
	def __init__(self: Self) -> NoneType:
		super().__init__()
		self.name = ""
		self.description = ""
		self.start_date = datetime.now().date()
		self.end_date = datetime.now().date()
		self.status = ""
		
	def acceptVisitor(self: Self, visitor: Any) -> Any:
		return visitor.visitProject(self)
		
class Resource(Model):
	
	def __init__(self: Self):
		super().__init__()
		self.name = ""
		
	def acceptVisitor(self: Self, visitor: Any) -> Any:
		return visitor.visitResource(self)
