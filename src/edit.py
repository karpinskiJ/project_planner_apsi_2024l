from answers import *
from database import DatabaseInterface
from contextlib import closing
from globs import authHandler

def edited(kind, model, item):
	with closing(DatabaseInterface()) as database:
		if hasattr(model, "uniqueName") and database.exists(kind, model.uniqueName()):
			return NameAlreadyExistsAnswer(kind, item, model)
		reason = model.nonConsistent()
		if reason:
			return NonConsistentErrorAnswer(reason)
		admin = False
		if kind == "user" and model.password:
			model.password = authHandler.hash(model.password)
			if item is None and database.empty("users"):
				admin = True
		database.edit(kind, model, item)
		database.commit()
		if admin:
			database.makeAdmin(model)
			database.commit()
	if item:
		return SuccessChangeAnswer(kind, model)
	else:
		return SuccessCreateAnswer(kind, model)
