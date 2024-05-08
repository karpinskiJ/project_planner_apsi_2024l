from database import DatabaseInterface
from contextlib import closing

class User:

	def __init__(self, login):
		self.login = login
		
	def __eq__(self, another):
		return self.login == another.login
		
	def inherits(self, another):
		with closing(DatabaseInterface()) as database:
			return database.inherits(self.login, another.login)
		
	def isAdmin(self):
		with closing(DatabaseInterface()) as database:
			return database.isAdmin(self.login) is not None
		
	def canDeleteUser(self, another):
		return ( self == another or self.isAdmin() and 
			( not another.isAdmin() or another.inherits(self) ) )
	
	def isOwner(self, project):
		with closing(DatabaseInterface()) as database:
			return database.isOwner(self.login, project)
	
	def haveProject(self):
		with closing(DatabaseInterface()) as database:
			return database.haveProject(self.login) is not None
			
	def canJoinProject(self, project):
		return not self.haveProject()
		
	def canEditProject(self, project = None):
		if project is None:
			return not self.haveProject()
		else:
			return self.isAdmin() or self.isOwner(project)
			
	def canEditResource(self, resource):
		return self.isAdmin()
