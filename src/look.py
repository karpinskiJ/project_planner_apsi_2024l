from answers import *
from database import DatabaseInterface
from contextlib import closing
from user import User
from models import fromSQL

def lookOneInternal(kind, item, user = None):
	if item is None:
		return PageNotExistAnswer()
	showProjectsOption = None
	if item == True:
		item = user
		showProjectsOption = False
	else:
		showProjectsOption = True
	user = User(user)
	model = None
	with closing(DatabaseInterface()) as database:
		model = database.modelOfName(kind, item)
	if model is None:
		return ItemNotExistsAnswer(kind, item)
	answer = OneAnswer(kind, fromSQL(kind, model))
	if kind == "user":
		if user.canDeleteUser(User(item)):
			answer.addButton("Delete user", "/delete?kind=user&item=" + item)
		if showProjectsOption:
			answer.addButton("Show projects", "/look?kind=project&of=user&item=" + item)
	elif kind == "project":
		if user.canJoinProject(item):
			answer.addButton("Join project", "/join?name=" + item)
		if user.canEdit("project", item):
			answer.addButton("Edit project", "/edit?kind=project&item=" + item)
			answer.addButton("Delete project", "/delete?kind=project&item=" + item)
		answer.addButton("Show resources", "/look?kind=resource&of=project&item=" + item)
		with closing(DatabaseInterface()) as interface:
			onwer = database.ownerOf(model)
			answer.addLink("Owner", owner, "/lookOne?kind=user&item=" + owner)
	elif kind == "resource":
		if user.canEdit("resource", item):
			answer.addButton("Edit resource", "/edit?kind=resource&item=" + item)
			answer.addButton("Delete resource", "/delete?kind=resource&item=" + item)
		answer.addButton("Show projects", "/look?kind=projects&of=resource&item=" + item)
	else:
		return PageNotExistAnswer()
	return answer
		
def lookInternal(kind, of, item, user = None):
	if of is not None and item is None:
		return PageNotExistAnswer()
	liste = None
	addProject = False
	if item == True:
		item = user
	with closing(DatabaseInterface()) as database:
		if kind == "project":
			if of == "user":
				liste = database.getProjectsOf(of, item)
				if item == True and User(user).canEditProject():
					item = user
					addProject = True
			elif of == "resource":
				liste = database.getProjectsOf(item)
			elif of is None:
				liste = database.getAllProjects()
			else:
				return PageNotExistAnswer()
		elif kind == "user":
			if of == "project":
				liste = database.getUsersOfProject(item)
			elif of is None:
				liste = database.getAllUsers()
			else:
				return PageNotExistAnswer()
		elif kind == "resource":
			if of == "project":
				liste = database.getResourcesOfProject(item)
			elif of is None:
				liste = database.getAllResources()
			else:
				return PageNotExistAnswer()
		else:
			return PageNotExistAnswer()
	answer = ListAnswer(kind, of, item, liste)
	if addProject:
		answer.addButton("Add project", "/add?kind=project")
	return answer
	
