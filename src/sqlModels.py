from sqlmodel import Field, SQLModel
from datetime import datetime, date
from typing import Optional, Self, Any

class Projects(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	name: str = Field(max_length=100)
	description: str
	start_date: date
	end_date: date
	status: str
	owner_id: int
    
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.login
		raise AttributeError(attr)
		
	def acceptVisitor(self: Self, visitor: Any) -> Any:
		return visitor.visitProject(self)
		
class Users(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	login: str = Field(max_length=50)
	password: str = Field(max_length=200)
	name: str = Field(max_length=50)
	surname: str = Field(max_length=50)
	role: str = Field(max_length=50)
	project_id: Optional[int]
	
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.login
		raise AttributeError(attr)
		
	def acceptVisitor(self: Self, visitor: Any) -> Any:
		return visitor.visitUser(self)

class Technical_Resources(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	name: str = Field(max_length=100)
	project_id: Optional[int]
	
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "uniqueName":
			return self.name
		raise AttributeError(attr)
		
	def acceptVisitor(self: Self, visitor: Any) -> Any:
		return visitor.visitResource(self)
		
class System_Admins(SQLModel, table = True):
	id: int = Field(primary_key = True)
	parent_id: Optional[int]
	promotion_time: datetime
