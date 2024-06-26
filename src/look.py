from answers import *
from contextlib import closing
from wraps import General, User
from visitors import LookOneVisitor, LinkVisitor
from widgets import Button, Link

def lookOneInternal(kind: str, item: str | bool | NoneType, user: str) -> Answer:
	if item is None:
		return PageNotExistAnswer()
	showProjectsOption = None
	if item == True:
		item = user
		showProjectsOption = False
	else:
		showProjectsOption = True
	user = User(user)
	# up there is promotion to wrap
	wrap = General.make(kind, item)
	# up there is promotion to wrap
	if not wrap.exists:
		return ItemNotExistsAnswer(kind, item)
	buttons = []
	links = []
	if kind == "user":
		if user.canDeleteUser(wrap) and user != wrap:
			buttons.append(Button("Delete user", "/delete?kind=user&item=" + item))
		if user == wrap:
			buttons.append(Button("Edit profile", "/edit?kind=user&item=" + item))
		if showProjectsOption:
			links.append(Link("Projects", "show", "/look?kind=project&of=user&item=" + item))
		if user.admin:
			if not wrap.admin:
				buttons.append(Button("Promote", "/promote?item=" + item))
			if wrap.admin and wrap.inherits(user):
				buttons.append(Button("Degrade", "/promote?item=" + item + "&promote=false"))
	elif kind == "project":
		links.append(Link("Owner", wrap.owner.login, "/lookOne?kind=user&item=" + wrap.owner.login))
		if wrap != user.project and user.canJoinProject(wrap):
			buttons.append(Button("Join project", "/join?name=" + item))
		if wrap == user.project and wrap.owner != user:
			buttons.append(Button("Leave project", "/join?name=" + item + "&join=false"))
		if user.canEdit("project", wrap):
			buttons.append(Button("Edit project", "/edit?kind=project&item=" + item))
			buttons.append(Button("Delete project", "/delete?kind=project&item=" + item))
		links.append(Link("Users", "show", "/look?kind=user&of=project&item=" + item))
		links.append(Link("Resources", "show", "/look?kind=resource&of=project&item=" + item))
	elif kind == "resource":
		if user.canEditResource(wrap):
			buttons.append(Button("Edit resource", "/edit?kind=resource&item=" + item))
			buttons.append(Button("Delete resource", "/delete?kind=resource&item=" + item))
		if user.owns:
			if not wrap.project:
				buttons.append(Button("Add to your project", "/compose?item=" + item))
			if user.project == wrap.project:
				buttons.append(Button("Release from your project",
					"/compose?item=" + item + "&compose=false"))
		links.append(Link("Projects", "show", "/look?kind=project&of=resource&item=" + item))
	else:
		return PageNotExistAnswer()
	return OneAnswer(kind, wrap.acceptVisitor(LookOneVisitor),
		links, buttons)
		
def lookInternal(kind: str, of: str | NoneType = None, 
	item: str | bool | NoneType = None, user: str | NoneType = None) -> Answer:
	if of is not None and item is None:
		return PageNotExistAnswer()
	addProject = False
	if item == True:
		item = user
	wrap = General.make(of, item) if of else None
	liste = None
	buttons = []
	if kind == "project":
		if of == "user":
			liste = [ wrap.project ] if wrap.project else []
			if item == user and User(user).canEditProject():
				buttons.append(Button("Add project", "/add?kind=project"))
		elif of == "resource":
			liste = [ wrap.project ] if wrap.project else []
		elif of is None:
			liste = General().all("project")
		else:
			return PageNotExistAnswer()
	elif kind == "user":
		if of == "project":
			liste = wrap.users
		elif of is None:
			liste = General().all("user")
		else:
			return PageNotExistAnswer()
	elif kind == "resource":
		if of == "project":
			liste = wrap.resources
		elif of is None:
			liste = General().all("resource")
			if User(user).canEditResource():
				buttons.append(Button("Add resource", "/add?kind=resource"))
		else:
			return PageNotExistAnswer()
	else:
		return PageNotExistAnswer()
	return ListAnswer(kind, of, item, [ wrape.acceptVisitor(LinkVisitor) for wrape in liste ], buttons)
	
