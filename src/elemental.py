import sqlModels as sql
import sqlmodel

def uniqueNameStr(kind: str) -> str:
	if kind == "user":
		return "login"
	else:
		return "name"

def uniqueNameField(kind: str) -> sqlmodel.Field:
	# here I don't know what exactly the return type is
	if kind == "user":
		return sql.Users.login
	elif kind == "project":
		return sql.Projects.name
	elif kind == "resource":
		return sql.TechnicalResources.name
		
def modelType(kind: str) -> sqlmodel.SQLModel:
	if kind == "user":
		return sql.Users
	elif kind == "project":
		return sql.Projects
	elif kind == "resource":
		return sql.TechnicalResources
