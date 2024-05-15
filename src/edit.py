from answers import *
from globs import authHandler
from inputModels import InputModel
from wraps import General, User
import wraps

def edited(kind: str, model: InputModel, item: str | NoneType = None,
	user: User | NoneType = None) -> Answer:
	print("item in edited: ", item)
	if hasattr(model, "uniqueName") and General().makeOfModel(model).exists:
		return NameAlreadyExistsAnswer(kind, item, model.uniqueName)
	if hasattr(model, "old") and not authHandler.verify(model.old, user.model.password):
		return BadPasswordAnswer()
	reason = model.notConsistent
	if reason:
		return NotConsistentAnswer(reason)
	admin = False
	if kind == "user" and hasattr(model, "password"):
		model.password = authHandler.hash(model.password)
		if item is None and General().empty("user"):
			admin = True
	General().edit(model, General.make(kind, item) if item else None)
	if kind == "project" and not item:
		user.project = wraps.Project(model)
	if admin:
		User(model).makeAdmin()
	newToken = ( authHandler.encodeToken(model.login) if
		kind == "user" and hasattr(model, "login") and model.login != item
		else None )
	if item:
		return SuccessChangeAnswer(kind, General().makeOfModel(model, item).uniqueName, newToken)
	else:
		return SuccessCreateAnswer(kind, General().makeOfModel(model).uniqueName)
