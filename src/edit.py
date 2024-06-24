from answers import *
from globs import authHandler
from inputModels import InputModel
from wraps import General, User
import wraps

def edited(kind: str, model: InputModel, item: str | NoneType = None,
	user: User | NoneType = None) -> Answer:
	if ( hasattr(model, "uniqueName") and item != model.uniqueName
		and General().makeOfModel(model).exists ):
		return NameAlreadyExistsAnswer(kind, item, model.uniqueName)
	if hasattr(model, "password"):
		model.password = authHandler.hash(model.password)
	General().edit(model, General.make(kind, item) if item else None)
	if kind == "project" and not item:
		user.addProject(wraps.Project(model))
	if item:
		return SuccessChangeAnswer(kind, General().makeOfModel(model, item).uniqueName)
	else:
		return SuccessCreateAnswer(kind, General().makeOfModel(model).uniqueName)
