from auth import AuthHandler
from globs import authHandler
from types import NoneType
from answers import ErrorAnswer

def receiveToken(token: str) -> str | NoneType:
	if not token:
		return None
	user = authHandler.decodeToken(token)
	if user == AuthHandler.expired or user == AuthHandler.invalid:
		return None
	return user
	
def checkToken(token: str) -> str | ErrorAnswer:
	if not token:
		return ErrorAnswer("You are not logged in", False)
	user = authHandler.decodeToken(token)
	if user == AuthHandler.expired:
		return ErrorAnswer("Your token expired", False)
	if user == AuthHandler.invalid:
		return ErrorAnswer("Invalid token", False)
	return user
