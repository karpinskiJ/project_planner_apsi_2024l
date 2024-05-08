from toEdit import ToEdit
from sqlModels import *
from widgets import Label

class Model:
	
	def __new__(cls, *args):
		if any([ field is None for field in args ]):
			return None
		obj = super().__new__(cls)
		obj.__init__(*args)
		return obj
		
	def nonConsistent(self):
		return None

class Project(Model):

	def __init__(self, name, description, start_date, end_date, status):
		self.name = name
		self.description = description
		self.start_date = start_date
		self.end_date = end_date
		self.status = status
		
	@staticmethod
	def fromSQL(sqlModel):
		return Project(sqlModel.name, sqlModel.description, sqlModel.start_date,
			sqlModel.end_date, sqlModel.status)
			
	def toSQL(self):
		return Projects(name = self.name, description = self.description, 
			start_date = self.start_date, end_date = self.end_date,
			status = self.status)
		
	def sentTo(self, sqlModel):
		sqlModel.name = self.name
		sqlModel.description = self.description
		sqlModel.start_date = self.start_date
		sqlModel.end_date = self.end_date
		sqlModel.status = self.status
		
	@staticmethod
	def toEdit(model):
		return [ 
			ToEdit("name", "Name", model.name if model else None),
			ToEdit("description", "Description", model.description if model else None),
			ToEdit("start_date", "Start date", model.start_date if model else None, "date"),
			ToEdit("end_date", "End date", model.end_date if model else None, "date"),
			ToEdit("status", "Status", model.status if model else None)
		]
		
	def look(self):
		return [ 
			Label("Name", self.name),
			Label("Description", self.description),
			Label("Start date", self.start_date),
			Label("End date", self.end_date),
			Label("Status", self.status)
			]
			
	def uniqueName(self):
		return self.name

class ShortUser(Model):

	def __init__(self, name, surname, role):
		self.name = name
		self.surname = surname
		self.role = role
		
	def sentTo(self, sqlModel):
		sqlModel.name = self.name
		sqlModel.surname = self.surname
		sqlModel.role = self.role
		
	@staticmethod
	def toEdit(model):
		return [
			ToEdit("name", "Name", model.name if model else None),
			ToEdit("surname", "Surname", model.surname if model else None),
			ToEdit("role", "Role", model.role if model else None)
		]
		
	def __getattr__(self, query):
		if query == "password":
			return None
		
class AdvancedUser(Model):
	
	def __init__(self, login, password):
		self.login = login
		self.password = password
		
	def sentTo(self, sqlModel):
		sqlModel.login = self.login
		sqlModel.password = self.password
		
	@staticmethod
	def toEdit(model):
		password = model.password if model else None
		return [
			ToEdit("login", "Login", model.login if model else None),
			ToEdit("password", "Password", password, typee = "password"),
			ToEdit("repeatedPassword", "Repeat password", password, typee = "password"),
		]
		
	def uniqueName(self):
		return self.login
		
class AdvancedUserRepeatedPassword(AdvancedUser):

	def __init__(self, login, password, repeatedPassword):
		super().__init__(login, password)
		self.repeatedPassword = repeatedPassword
		
	def nonConsistent(self):
		if self.password != self.repeatedPassword:
			return "passwords"
		else:
			return None
		
class DisplayUser(Model):
	
	def __init__(self, login, shortUser):
		self.login = login
		self.shortUser = shortUser
		
	def look(self):
		return [ Label("Login", self.login),
			Label("Name", self.shortUser.name),
			Label("Surname", self.shortUser.surname),
			Label("Role", self.shortUser.role)
			]
			
	@staticmethod
	def fromSQL(sqlModel):
		return DisplayUser(sqlModel.login, ShortUser(sqlModel.name, sqlModel.surname, sqlModel.role))
		
class FullUser(Model):

	def __init__(self, advancedUser, shortUser):
		self.advancedUser = advancedUser
		self.shortUser = shortUser

	@staticmethod
	def toEdit(model):
		return ( AdvancedUser.toEdit(model.advancedUser if model else None)
			+ ShortUser.toEdit(model.shortUser if model else None))
			
	def __getattr__(self, query):
		if query == "password":
			return self.advancedUser.password
			
	def __setattr__(self, query, value):
		if query == "password":
			self.advancedUser.password = value
		else:
			self.__dict__[query] = value
	
	def uniqueName(self):
		return self.advancedUser.login
		
	def toSQL(self):
		return Users(login = self.advancedUser.login, password = self.advancedUser.password, 
			name = self.shortUser.name, surname = self.shortUser.surname, role = self.shortUser.role)
		
class Resource(Model):

	def __init__(self, name):
		self.name = name
	
	@staticmethod
	def fromSQL(sqlModel):
		return Resource(sqlModel.name)
		
	def toSQL(self):
		return Technical_Resources(name = self.name)
		
	def sentTo(self, sqlModel):
		sqlModel.name = self.name
	
	@staticmethod
	def toEdit(model):
		return [
			ToEdit("name", "Name", model.name if model else None)
			]
	
	def look(self):
		return [ Label("Name", self.name) ]
		
	def uniqueName(self):
		return self.uniqueName()
		
def makeUser(logged, advanced, login, password,
	repeatedPassword, name, surname, role):
	if logged:
		if advanced:
			print("Here")
			return AdvancedUserRepeatedPassword(login, password, repeatedPassword)
		else:
			return ShortUser(name, surname, role)
	else:
		return FullUser(AdvancedUserRepeatedPassword(login, password, repeatedPassword),
			ShortUser(name, surname, role))
			
def fromSQL(kind, model):
	if kind == "user":
		return DisplayUser.fromSQL(model)
	elif kind == "project":
		return Project.fromSQL(model)
	elif kind == "resource":
		return Project.fromSQL(model)

