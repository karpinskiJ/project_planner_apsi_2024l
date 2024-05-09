from services import *
from sqlmodel import Session, select
from sqlModels import *
import sqlModels

class DatabaseException(Exception):
	pass

class DatabaseInterface:

	def __init__(self):
		self.session = Session(get_engine())
		
	def modelOfName(self, kind, name):
		print(kind)
		return (self.session.exec(select(model(kind)).where(sqlModels.titleField(kind) == name)).
			first())
	
	def exists(self, kind, name):
		return self.modelOfName(kind, name) is not None
		
	def idOfName(self, kind, name):
		return self.modelOfName(kind, name).id
	
	def isAdmin(self, user):
		ide = self.idOfName("user", user)
		if ide is None:
			raise DatabaseException()
		return self.session.exec(select(Admins.id).where(Admins.id == ide)).first()
		
	def inherits(self, user, another):
		another = self.isAdmin(another)
		user = self.isAdmin(user)
		while user is not None:
			user = self.session.exec(select(Admins.parent_id).where(Admins.id == user)).first()
			if user == another:
				return True
		return False
		
	def isOwner(self, user, project):
		return (self.session.exec(select(Projects.owner_id).where(Projects.name == project))
			.first() == idOfName(user))
			
	def haveProject(self, user):
		return (self.session.exec(select(Users.project_id).where(Users.name == user))
			.first())
			
	def edit(self, kind, model, item):
		if item is None:
			self.session.add(model.toSQL())
		else:
			old = self.modelOfName(kind, item)
			model.sentTo(old)
			self.session.add(old)
	
	def delete(self, kind, item):
		self.session.delete(self.modelOfName(kind, item))
		
	def add(self, model):
		self.session.add(model)
		
	def makeAdmin(self, user, parent = None):
		user = self.idOfName("user", user.login)
		parent = self.idOfName("user", parent.login)
		self.session.add(Admin(user, parent))
	
	def close(self):
		self.session.close()
	
	def commit(self):
		self.session.commit()
		
	def getProjectsOf(self, kind, item):
		return (self.session.exec(select(Projects.name).
				where(Projects.id == self.modelOfName(kind, item).project_id)).all())
		
	def getAllProjects(self):
		return self.session.exec(select(Projects.name)).all()
		
	def getUsersOfProject(self, model):
		return (self.session.exec(select(Users.login).
			where(Users.project_id == model.id)).all())
			
	def getAllUsers(self):
		return self.session.exec(select(Users.login)).all()
	
	def getResourcesOfProject(self, model):
		return (self.session.exec(select(Technical_Resources.name).
			where(Technical_Resources.project_id == model.id)).all())
			
	def getAllResources(self):
		return self.session.exec(select(Technical_Resources.name)).all()
		
	def empty(self, kind):
		if kind == "user":
			return len(self.getAllUsers()) == 0
		elif kind == "project":
			return len(self.getAllProjects()) == 0
		elif kind == "resource":
			return len(self.getAllResources()) == 0
