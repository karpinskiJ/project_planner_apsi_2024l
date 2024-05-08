from sqlmodel import Field, SQLModel
from datetime import datetime, date
from typing import Optional

class Projects(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	name: str = Field(max_length=100)
	description: str
	start_date: date
	end_date: date
	status: str
    
	def uniqueName(self):
		return self.name
		
class Users(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	login: str = Field(max_length=50)
	password: str = Field(max_length=200)
	name: str = Field(max_length=50)
	surname: str = Field(max_length=50)
	role: str = Field(max_length=50)
	project_id: Optional[int]
	
	def uniqueName(self):
		return self.login

class Technical_Resources(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	name: str = Field(max_length=100)
	project_id: Optional[int]

	def uniqueName(self):
		return self.name

class Admins(SQLModel, table = True):
	id: int = Field(primary_key = True)
	super_id: Optional[int]
	
def titleStr(kind):
	if kind == "user":
		return "login"
	else:
		return "name"
		
def titleField(kind):
	print("kind:", kind)
	if kind == "user":
		return Users.login
	elif kind == "project":
		return Project.name
	elif kind == "resource":
		return Technical_Resources.name
		
def model(kind):
	if kind == "user":
		return Users
	elif kind == "project":
		return Projects
	elif kind == "resource":
		return Technical_Resources
