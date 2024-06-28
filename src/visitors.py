import widgets
from widgets import Label, ToEdit, Button
import sqlModels as sql
import wraps
import empty

class LookOneVisitor:
	# This visitor visits SQL models
	# for display in lookOne

	@staticmethod
	def visitProject(project: wraps.Project) -> list[widgets.Label]:
		model = project.model
		return [
			Label("Name", model.name),
			Label("Description", model.description),
			Label("Start date", model.start_date),
			Label("End date", model.end_date),
			Label("Status", model.status.value)
			]
			
	@staticmethod
	def visitUser(user: wraps.User, *, advanced: bool = False) -> list[widgets.Label]:
		model = user.model
		return [
			Label("Login", model.login),
			Label("Name", model.name),
			Label("Surname", model.surname),
			Label("Role", model.role.value)
		]
		
	@staticmethod
	def visitResource(resource: wraps.Resource) -> list[widgets.Label]:
		model = resource.model
		return [
			Label("Name", model.name),
			Label("Type", model.type.value)
			]
			
class ToEditVisitor:
	# This visitor visits wraps and empties
	# for generating text frames for data inputing
	
	@staticmethod
	def visitProject(project: wraps.Project | empty.Project) -> list[widgets.ToEdit]:
		model = project.model
		return [
			ToEdit("name", "Name", model.name),
			ToEdit("description", "Description", model.description),
			ToEdit("start_date", "Start date", model.start_date, "date"),
			ToEdit("end_date", "End date", model.end_date, "date"),
			ToEdit("status", "Status", model.status.value,
				options = [ e.value for e in sql.ProjectStatus ])
			]
	
	@staticmethod
	def visitUser(user: wraps.User | empty.User) -> list[widgets.ToEdit]:
		model = user.model
		return [
			ToEdit("login", "Login", model.login),
			ToEdit("name", "Name", model.name),
			ToEdit("surname", "Surname", model.surname),
			ToEdit("manager", "Manager", user.manager, 
				options = [""] + wraps.General().managers)
			]
		
	@staticmethod
	def visitResource(resource: wraps.Resource | empty.Resource) -> list[widgets.ToEdit]:
		model = resource.model
		return [
			ToEdit("name", "Name", model.name),
			ToEdit("type", "Type", model.type.value,
				options = [ e.value for e in sql.ResourceType ])
			]
			
	@staticmethod
	def visitLogin() -> list[widgets.ToEdit]:
		return [
			ToEdit("login", "Login", ""),
			ToEdit("password", "Password", "", typee = "password")
			]
	
	@staticmethod
	def visitCommit() -> list[widgets.ToEdit]:
		return [
			ToEdit("password", "Type password", "", typee = "password")
		]
		
	@staticmethod
	def visitChangePassword() -> list[widgets.ToEdit]:
		return [
			ToEdit("old", "Old password", "", typee = "password"),
			ToEdit("password", "New password", "", typee = "password"),
			ToEdit("repeated", "Repeated password", "", typee = "password")
		]
		
class LinkVisitor:
	# This visitor visits wraps
	# for getting their unique names
	# and making hyperlinks of them
	
	@staticmethod
	def visitProject(wrap: wraps.Project) -> widgets.Button:
		return Button(wrap.name, "/lookOne?kind=project&item=" + wrap.name)
		
	@staticmethod
	def visitUser(wrap: wraps.User, *, advanced = False) -> widgets.Button:
		return Button(wrap.login, "/lookOne?kind=user&item=" + wrap.login)
		
	@staticmethod
	def visitResource(wrap: wraps.Resource) -> widgets.Button:
		return Button(wrap.name, "/lookOne?kind=resource&item=" + wrap.name)
