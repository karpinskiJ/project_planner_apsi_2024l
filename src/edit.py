from answers import *
from database import DatabaseInterface
from contextlib import closing
from globs import authHandler

def edited(kind, model, item):
	changeLogin = None
	with closing(DatabaseInterface()) as database:
		if hasattr(model, "uniqueName") and database.exists(kind, model.uniqueName()):
			return NameAlreadyExistsAnswer(kind, item, model)
		reason = model.nonConsistent()
		if reason:
			return NonConsistentErrorAnswer(reason)
		admin = False
		if kind == "user" and model.password:
			model.password = authHandler.hash(model.password)
			if item is None and database.empty("user"):
				admin = True
		database.edit(kind, model, item)
		database.commit()
		if admin:
			database.makeAdmin(model)
			database.commit()
		changeLogin = kind == "user" and hasattr(model, "login") and model.login != item
	if item:
		return SuccessChangeAnswer(kind, model, changeLogin)
	else:
		return SuccessCreateAnswer(kind, model)
