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
			Label("Status", model.status)
			]
			
	@staticmethod
	def visitUser(user: wraps.User, *, advanced: bool = False) -> list[widgets.Label]:
		model = user.model
		return [
			Label("Login", model.login),
			Label("Name", model.name),
			Label("Surname", model.surname),
			Label("Role", model.role),
			Label("Position", user.position)
		]
		
	@staticmethod
	def visitResource(resource: wraps.Resource) -> list[widgets.Label]:
		model = resource.model
		return [
			Label("Name", model.name)
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
			ToEdit("status", "Status", model.status)
			]
	
	@staticmethod
	def visitUser(user: wraps.User | empty.User, *, advanced: bool,
		old: bool = True,
		required: bool = False) -> list[widgets.ToEdit]:
		model = user.model
		if advanced:
			returnal = [
				ToEdit("old", "Old password", "", "password")
				] if old else []
			return returnal + [
				ToEdit("login", "Login", model.login),
				ToEdit("password", "Password", "", "password", required = required),
				ToEdit("repeated", "Repeat password", "", "password", required = required)
				]
		else:
			return [
				ToEdit("name", "Name", model.name),
				ToEdit("surname", "Surname", model.surname),
				ToEdit("role", "Role", model.role)
				]
				
	@staticmethod
	def visitEmptyUser(user: empty.User) -> list[widgets.ToEdit]:
		return (ToEditVisitor.visitUser(user, advanced = True, old = False, required = True)
			+ ToEditVisitor.visitUser(user, advanced = False) )
		
	@staticmethod
	def visitResource(resource: wraps.Resource | empty.Resource) -> list[widgets.ToEdit]:
		model = resource.model
		return [
			ToEdit("name", "Name", model.name)
			]
			
	@staticmethod
	def visitLogin() -> list[widgets.ToEdit]:
		return [
			ToEdit("login", "Login", ""),
			ToEdit("password", "Password", "", typee = "password")
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
