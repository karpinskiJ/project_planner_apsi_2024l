from globs import templates
import copy
import elemental
from typing import Self
from types import NoneType
from fastapi import Request
from fastapi.responses import HTMLResponse
import widgets
from widgets import ToEdit

class Answer:

	def __init__(self: Self, template: str, title: str, logged: bool = True) -> NoneType:
		self.variables = { title : "title" }
		self.template = template
		self.logged = logged
		
	def toHTML(self: Self, request: Request, logged: bool = True) -> HTMLResponse:
		variables = copy.copy(self.variables)
		variables['request'] = request
		variables['logged'] = self.logged and logged
		response = templates.TemplateResponse(self.template, variables)
		if hasattr(self, "newToken"):
			response.set_cookie(key = "token", value = self.newToken)
		return response
		
class MessageAnswer(Answer):

	def __init__(self: Self, title: str, message: str, logged: bool = True) -> NoneType:
		super().__init__("message.html", title)
		self.variables['message'] = message
		
class ErrorAnswer(MessageAnswer):

	def __init__(self: Self, message: str, logged: bool = True) -> NoneType:
		super().__init__("Sorry", message, logged)
		self.variables['error'] = True
		
class SuccessAnswer(MessageAnswer):
	
	def __init__(self: Self, message: str, logged: bool = True) -> NoneType:
		super().__init__("Got it", message, logged)
		self.variables['error'] = False
		
class PageNotExistAnswer(ErrorAnswer):

	def __init__(self: Self) -> NoneType:
		super().__init__("Requested page does not exist")
		
class AlreadyLoggedInAnswer(ErrorAnswer):

	def __init__(self: Self) -> NoneType:
		super().__init__("You are already logged in")
		
class CannotCreateAnswer(ErrorAnswer):

	def __init__(self: Self, kind: str) -> NoneType:
		super().__init__("Cannot create " + kind)
		
class CannotChangeAnswer(ErrorAnswer):

	def __init__(self: Self, kind: str, item: str) -> NoneType:
		super().__init__("Cannot change " + kind + ": " + item)
		
class CannotDeleteAnswer(ErrorAnswer):

	def __init__(self: Self, kind: str, item: str) -> NoneType:
		super().__init__("Cannot delete " + kind + ": " + item)
		
class SuccessCreateAnswer(SuccessAnswer):

	def __init__(self: Self, kind: str, item: str) -> NoneType:
		super().__init__("Successfully created " + kind + ": " + item)
		
class SuccessChangeAnswer(SuccessAnswer):
	
	def __init__(self: Self, kind: str, item: str, newToken: str) -> NoneType:
		super().__init__("Successfully changed " + kind + ": " + item)
		if newToken:
			self.newToken = newToken
		
class SuccessDeleteAnswer(SuccessAnswer):
	
	def __init__(self: Self, kind: str, item: str):
		super().__init__("Successfully deleted " + kind + ": " + item)
		
def editMessageHeader(kind: str, item: str) -> tuple[str, str | NoneType, str | NoneType]:
	if not item:
		return "Create " + kind, None, None
	else:
		return "Change " + kind, None, None
		
class ToEditAnswer(Answer):

	def __init__(self: Self, kind: str,
		toEdits: list[widgets.ToEdit], item: str | NoneType = None, *,
		advanced: bool = False) -> NoneType:
		title, header, subheader = editMessageHeader(kind, item)
		super().__init__("edit.html", title)
		self.variables['liste'] = toEdits
		target = '/' + kind
		if item:
			target += '?item=' + item
		if advanced:
			target += "&advanced=true"
		self.variables['target'] = target
		self.variables['header'] = header
		self.variables['subheader'] = subheader
		enter = None
		if not item:
			if kind == "user":
				enter = "Register"
			else:
				enter = "Create"
		else:
			enter = "Change"
		self.variables['enter'] = enter
		
class NameAlreadyExistsAnswer(ErrorAnswer):
	
	def __init__(self: Self, kind: str, item: str,
		existing: str) -> NoneType:
		nameOfKind = elemental.uniqueNameStr(kind)
		ending = nameOfKind.capitalize() + " \"" + existing + "\" already exists."
		if item:
			super().__init__("Cannot change " + nameOfKind + " for " + item + ".\n"
				+ ending)
		else:
			super().__init__("Cannot set " + nameOfKind + ".\n" + ending)

class NotConsistentAnswer(ErrorAnswer):
	
	def __init__(self: Self, reason: str | NoneType = None) -> NoneType:
		if reason == "passwords":
			super().__init__("Passwords do not fit")
		else:
			super().__init__("Data inconsinstence")

class ItemNotExistsAnswer(ErrorAnswer):

	def __init__(self: Self, kind: str, item: str) -> NoneType:
		super().__init__(kind.capitalize() + " of " + elemental.uniqueNameStr(kind) + " " + item
			+ " does not exist")

def loginMessageHeader() -> tuple[str, str | NoneType, str | NoneType]:
	return "Login", None, None
	
class ToLoginAnswer(Answer):
	
	def __init__(self: Self, toEdits: list[widgets.ToEdit]) -> NoneType:
		title, header, subheader = loginMessageHeader()
		super().__init__("edit.html", title, False)
		self.variables['liste'] = toEdits
		self.variables['target'] = '/logged'
		self.variables['header'] = header
		self.variables['subheader'] = subheader
		self.variables['enter'] = "Log in"
	
def commitMessageHeader() -> tuple[str, str | NoneType, str | NoneType]:
	return "Commit", None, None
	
class CommitAnswer(Answer):

	def __init__(self: Self, toEdits: list[widgets.ToEdit], target: str) -> NoneType:
		title, header, subheader = commitMessageHeader()
		super().__init__("edit.html", title)
		self.variables['liste'] = toEdits
		self.variables['target'] = target
		self.variables['header'] = header
		self.variables['subheader'] = subheader
		self.variables['enter'] = "Commit"
		
class BadPasswordAnswer(ErrorAnswer):
	
	def __init__(self: Self) -> NoneType:
		super().__init__("Bad password", False)
		
class CannotJoinProjectAnswer(ErrorAnswer):

	def __init__(self: Self, name: str) -> NoneType:
		super().__init__("Cannot join project " + name)
		
class LookAnswer(Answer):
	
	def __init__(self: Self, template: str, title: str, buttons: list[widgets.Button]) -> NoneType:
		super().__init__(template, title)
		self.variables['buttons'] = buttons
		
class OneAnswer(LookAnswer):

	def __init__(self: Self, kind: str, fields: list[widgets.Label], links: list[widgets.Link],
		buttons: list[widgets.Button]) -> NoneType:
		super().__init__("one.html", kind.capitalize(), buttons)
		self.variables['links'] = links
		self.variables['fields'] = fields

class ListAnswer(LookAnswer):
	
	def __init__(self: Self, kind: str, of: str, item: str,
		liste: list[widgets.Button], buttons: list[widgets.Button]) -> NoneType:
		title = kind.capitalize()
		if of:
			title += " of " + of + " " + item
		super().__init__("liste.html", title, buttons)
		self.variables['liste'] = liste
		self.variables['kind'] = kind
		
class LackOfFieldsAnswer(ErrorAnswer):
	
	def __init__(self: Self, kind: str, item: str) -> NoneType:
		super().__init__("Lack of fields in " + kind)

class NotInProjectAnswer(ErrorAnswer):

	def __init__(self: Self, name: str) -> NoneType:
		super().__init__("You are not participating project: " + name)
		
class AlreadyInProjectAnswer(ErrorAnswer):

	def __init__(self: Self, name: str) -> NoneType:
		super().__init__("You are already participating project: " + name)

class SuccessPromoteAnswer(SuccessAnswer):

	def __init__(self: Self, name: str) -> NoneType:
		super().__init__("Successfully promoted user: " + name)
		
class CannotPromoteAnswer(ErrorAnswer):

	def __init__(self: Self, name: str) -> NoneType:
		super().__init__("Cannot promote user: " + name)
		
class SuccessDegradeAnswer(SuccessAnswer):
	
	def __init__(self: Self, name: str) -> NoneType:
		super().__init__("Successfully degrade user: " + name)
		
class CannotDegradeAnswer(ErrorAnswer):

	def __init__(self: Self, name: str) -> NoneType:
		super().__init__("Cannot degrade user " + name)
