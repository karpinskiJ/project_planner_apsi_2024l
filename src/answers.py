from globs import templates
import copy
from toEdit import ToEdit
from sqlModels import titleStr
from widgets import *
from globs import authHandler

class Answer:

	def __init__(self, template, title, logged = True):
		self.variables = { title : "title" }
		self.template = template
		self.logged = logged
		
	def toHTML(self, request, logged = True):
		variables = copy.copy(self.variables)
		variables['request'] = request
		variables['logged'] = self.logged and logged
		response = templates.TemplateResponse(self.template, variables)
		if hasattr(self, "newLogin"):
			response.set_cookie(key = "token", value = authHandler.encodeToken(self.newLogin))
		return response
		
class MessageAnswer(Answer):

	def __init__(self, title, message, logged = True):
		super().__init__("message.html", title)
		self.variables['message'] = message
		
class ErrorAnswer(MessageAnswer):

	def __init__(self, message, logged = True):
		super().__init__("Sorry", message, logged)
		self.variables['error'] = True
		
class SuccessAnswer(MessageAnswer):
	
	def __init__(self, message, logged = True):
		super().__init__("Got it", message, logged)
		self.variables['error'] = False
class PageNotExistAnswer(ErrorAnswer):

	def __init__(self):
		super().__init__("Requested page does not exist")
		
class AlreadyLoggedInAnswer(ErrorAnswer):

	def __init__(self):
		super().__init__("You are already logged in")
		
class CannotCreateAnswer(ErrorAnswer):

	def __init__(self, kind):
		super().__init__("Cannot create " + kind)
		
class CannotChangeAnswer(ErrorAnswer):

	def __init__(self, kind, item):
		super().__init__("Cannot change " + kind + ": " + item)
		
class CannotDeleteAnswer(ErrorAnswer):

	def __init__(self, kind, item):
		super().__init__("Cannot delete " + kind + ": " + item)
		
class SuccessCreateAnswer(SuccessAnswer):

	def __init__(self, kind, model):
		super().__init__("Successfully created " + kind + ": " + model.uniqueName())
		
class SuccessChangeAnswer(SuccessAnswer):
	
	def __init__(self, kind, model, changeLogin):
		super().__init__("Successfully changed " + kind + ": " + model.uniqueName())
		if changeLogin:
			self.newLogin = model.login
		
class SuccessDeleteAnswer(SuccessAnswer):
	
	def __init__(self, kind, model):
		super().__init__("Successfully deleted " + kind + ": " + model.uniqueName())
		
def editMessageHeader(kind, model):
	if model:
		return "Change " + kind, None, None
	else:
		return "Create " + kind, None, None
		
class ToEditAnswer(Answer):

	def __init__(self, kind, model = None, advanced = False):
		title, header, subheader = editMessageHeader(kind, model)
		super().__init__("edit.html", title)
		self.variables['liste'] = ToEdit.toEdit(kind, model, advanced)
		target = '/' + kind
		if model:
			target += '?item=' + model.uniqueName()
		print("advanced1: ", advanced)
		if advanced:
			target += "&advanced=true"
		self.variables['target'] = target
		self.variables['header'] = header
		self.variables['subheader'] = subheader
		self.variables['enter'] = "Register" if kind == "user" and not model else "Change"
		
class NameAlreadyExistsAnswer(ErrorAnswer):
	
	def __init__(self, kind, item, model):
		name = model.uniqueName()
		nameOfKind = titleStr(kind)
		ending = nameOfKind.capitalize() + " \"" + name + "\" already exists."
		if item:
			super().__init__("Cannot change " + nameOfKind + " for " + item + ".\n"
				+ ending)
		else:
			super().__init__("Cannot set " + nameOfKind + ".\n" + ending)

class NonConsistentErrorAnswer(ErrorAnswer):
	
	def __init__(self, reason):
		if reason == "passwords":
			super().__init__("Passwords do not fit")
		else:
			super().__init__("Data inconsinstence")

class ItemNotExistsAnswer(ErrorAnswer):

	def __init__(self, kind, item):
		super().__init__(kind.capitalize() + " of " + titleStr(kind) + " " + item
			+ " does not exist")

def loginMessageHeader():
	return "Login", None, None
	
class ToLoginAnswer(Answer):
	
	def __init__(self):
		title, header, subheader = loginMessageHeader()
		super().__init__("edit.html", title, False)
		self.variables['liste'] = [
			ToEdit("login", "Login"),
			ToEdit("password", "Password", typee = "password")
			]
		self.variables['target'] = '/logged'
		self.variables['header'] = header
		self.variables['subheader'] = subheader
		self.variables['enter'] = "Log in"
		
class BadPasswordAnswer(ErrorAnswer):
	
	def __init__(self):
		super().__init__("Bad password", False)
		
class CannotJoinProjectAnswer(ErrorAnswer):

	def __init__(self, name):
		super().__init__("Cannot join project " + name)
		
class LookAnswer(Answer):
	
	def __init__(self, title, template):
		super().__init__(template, title)
		self.variables['buttons'] = []
		
	def addButton(self, text, link):
		self.variables['buttons'].append(Button(text, link))
		
class OneAnswer(LookAnswer):

	def __init__(self, kind, model):
		super().__init__(kind.capitalize(), "one.html")
		self.variables['links'] = []
		self.variables['fields'] = model.look()
	
	def addLink(self, label, text, link):
		self.variables['links'].append(Link(label, text, link))

class ListAnswer(LookAnswer):
	
	def __init__(self, kind, of, item, liste):
		title = kind.capitalize()
		if of:
			title += " of " + of + " " + item
		super().__init__(title, "liste.html")
		self.variables['liste'] = liste
		self.variables['kind'] = kind
		
class LackOfFieldsAnswer(ErrorAnswer):
	
	def __init__(self, kind, item):
		super().__init__("Lack of fields in " + kind)
