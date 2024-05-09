import models

from fastapi import FastAPI, Request, Form, Path, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from typing import Annotated
import datetime
import os
from answers import *
from look import *
from edit import *
from sqlModels import *
from models import *
from user import User
from database import DatabaseInterface
from globs import app, authHandler, AuthHandler
from contextlib import closing

def receiveToken(token):
	if not token:
		return None
	user = authHandler.decodeToken(token)
	if user == AuthHandler.expired or user == AuthHandler.invalid:
		return None
	return user
	
def checkToken(token):
	if not token:
		return ErrorAnswer("You are not logged in", False)
	user = authHandler.decodeToken(token)
	if user == AuthHandler.expired:
		return ErrorAnswer("Your token expired", False)
	if user == AuthHandler.invalid:
		return ErrorAnswer("Invalid token", False)
	return user
	
@app.get('/', response_class = Response)
def main(request: Request, token: Annotated[str, Cookie()] = None):
	if receiveToken(token):
		return RedirectResponse('/dashboard?kind=user')
	return Answer('main.html', "Welcome").toHTML(request, False)

@app.get('/login', response_class = HTMLResponse)
def login(request: Request, token: Annotated[str, Cookie()] = None):
	if receiveToken(token):
		return AlreadyLoggedInAnswer().toHTML(request)
	return ToLoginAnswer().toHTML(request)
    
@app.get('/register', response_class = HTMLResponse)
def register(request: Request, token: Annotated[str, Cookie()] = None):
	if receiveToken(token):
		return AlreadyLoggedInAnswer().toHTML(request)
	return ToEditAnswer("user").toHTML(request, False)

@app.get('/delete', response_class = HTMLResponse)
def delete(request: Request, kind: Annotated[str, Query()] = None,
	item: Annotated[str, Query()] = None, token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind is None:
		return PageNotExistAnswer().toHTML(request)
	if item == None:
		if kind != "project":
			return PageNotExistAnswer().toHTML(request)
		else:
			item = user
	with closing(DatabaseInterface()) as database:
		if not database.exists(kind, item):
			return ItemNotExistsAnswer(kind, item).toHTML(request)
	user = User(user)
	if kind == "user":
		if not user.canDeleteUser(item):
			return CannotDeleteAnswer("user", item).toHTML(request)
	else:
		if not user.canEdit(kind, item):
			return CannotDeleteAnswer(kind, item).toHTML(request)
	with closing(DatabaseInterface()) as database:
		database.delete(kind, item)
	return SuccessDeleteAnswer(kind, item).toHTML(request)
		
@app.get('/create', response_class = HTMLResponse)
def create(request: Request, kind: Annotated[str, Query()] = None,
	token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind != "project" and kind != "resource":
		return PageNotExistAnswer().toHTML(request)
	if not User(user).canEdit(kind):
		return CannotCreateAnswer(kind)
	return ToEditAnswer(kind).toHTML(request)

@app.get('/edit', response_class = HTMLResponse)
def edit(request: Request, kind: Annotated[str, Query()] = None,
	item: Annotated[str, Query()] = None,
	advanced: Annotated[bool, Query()] = False,
	token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind == "user" and item is None:
		item = user
	if kind != "project" and kind != "resource" and kind != "user" or item is None:
		return PageNotExistAnswer().toHTML(request)
	with closing(DatabaseInterface()) as database:
		if not database.exists(kind, item):
			return ItemNotExistsAnswer(kind, item).toHTML(request)
	if kind == "user":
		if item != user:
			return CannotEditAnswer("user", item).toHTML(request)
	else:
		if not User(user).canEdit(kind, item):
			return CannotEditAnswer(kind, item).toHTML(request)
	with closing(DatabaseInterface()) as database:
		return ToEditAnswer(kind, database.modelOfName(kind, item), advanced).toHTML(request)
		
@app.post('/user', response_class = HTMLResponse)
def user(request: Request, login: Annotated[str, Form()] = None, 
	password: Annotated[str, Form()] = None, repeatedPassword: Annotated[str, Form()] = None,
	name: Annotated[str, Form()] = None, surname: Annotated[str, Form()] = None,
	role: Annotated[str, Form()] = None,
	advanced: Annotated[bool, Query()] = False,
	token: Annotated[str, Cookie()] = None):
		print("advanced: ", advanced)
		item = receiveToken(token)
		logged = item is not None
		model = makeUser(logged, advanced, login, password,
			repeatedPassword, name, surname, role)
		if model is None:
			return LackOfFieldsAnswer("user", item).toHTML(request, logged)
		edite = edited("user", model, item)
		if advanced:
			edite.variables['advanced'] = True
		return edite.toHTML(request, logged)
			
@app.post('/project', response_class = HTMLResponse)
def project(request: Request, name: Annotated[str, Form()] = None, 
	description: Annotated[str, Form()] = None,
	start_date: Annotated[str, Form()] = None,
	end_date: Annotated[str, Form()] = None,
	status: Annotated[str, Form()] = None, 
	item: Annotated[str, Query()] = None, token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	model = Project(name, description, datetime.date(start_date), datetime.date(end_date), status)
	if model is None:
		return LackOfFieldsAnswer("project", item).toHTML(request)
	if not User(user).canEdit("project", item):
		return CannotChangeAnswer("project", item).toHTML(request)
	return edited("project", model, item).toHTML(request)
	
@app.post('/resource', response_class = HTMLResponse)
def resource(request: Request, name: Annotated[str, Form()] = None,
	item: Annotated[str, Query()] = None, token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toResponse(request)
	model = makeResource(name)
	if model is None:
		return LackOfFieldsAnswer("resource", item).toHTML(request)
	if not User(user).canEdit("resource", item):
		return CannotChangeAnswer("resource", item).toHTML(request)
	return edited("resource", model, item).toHTML(request)
	
	
@app.post('/logged', response_class = Response)
def logged(request: Request, 
	login: Annotated[str, Form()] = None,
	password: Annotated[str, Form()] = None):
	if login is None or password is None:
		return PageNotExistAnswer().toHTML(request, False)
	with closing(DatabaseInterface()) as database:
		model = database.modelOfName("user", login)
		if not model:
			return ItemNotExistsAnswer("user", login).toHTML(request, False)
		if not authHandler.verify(password, model.password):
			return BadPasswordAnswer().toHTML(request)
	response = RedirectResponse("/dashboard?kind=user")
	response.set_cookie(key = "token", value = authHandler.encodeToken(login))
	response.status_code = 302
	return response

@app.get('/add', response_class = HTMLResponse)
def add(request: Request, kind: Annotated[str, Query()] = None,
	token: Annotated[str, Cookie()] = None):
	user = checkToken(token, request)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind != "project" and kind != "resource":
		return PageNotExistAnswer().toHTML(request)
	if not User(user).canEdit(kind):
		return CannotCreateAnswer(kind).toHTML(request)
	return ToEditAnswer("project").toHTML(request)
	
@app.get('/join', response_class = Response)
def join(request: Request, name: Annotated[str, Query()] = None,
	token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if name is None:
		return PageNotExistAnswer().toHTML(request)
	if User(user).canJoinProject():
		with closing(DatabaseInterface()) as database:
			project = database.modelOfName("project", name)
			user.project_id = project.id
			database.add(user)
			database.commit()
			return RedirectResponse("/dashboard?kind=project")
	else:
		return CannotJoinProjectAnswer(name).toHTML(request)

@app.get('/dashboard', response_class = HTMLResponse)
def dashboard(request: Request, kind: Annotated[str, Query()] = None,
	token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind == "user":
		return lookOneInternal("user", True, user).toHTML(request)
	elif kind == "project":
		return lookInternal("project", "user", True, user).toHTML(request)

@app.get('/lookOne', response_class = HTMLResponse)
def lookOne(request: Request, kind: Annotated[str, Query()] = None,
	item: Annotated[str, Query()] = None, token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	return lookOneInternal(kind, item).toHTML(request)

@app.get('/look', response_class = HTMLResponse)
def look(request: Request, kind: Annotated[str, Query()] = None,
	of: Annotated[str, Query()] = None,
	item: Annotated[str, Query()] = None,
	token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	return lookInternal(kind, of, item).toHTML(request)

@app.get('/logout', response_class = Response)
def logout(request: Request, token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML()
	response = RedirectResponse('/')
	response.delete_cookie("token")
	return response

@app.get('/advanced', response_class = HTMLResponse)
def advanced(request: Request, token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML()
	return Answer("advanced.html", "Advanced").toHTML(request)

@app.get('/{resource}', response_class = Response)
def getResource(request: Request, resource: Annotated[str, Path()],
	token: Annotated[str, Cookie()] = None):
	filename = "templates/" + resource
	if not os.path.isfile(filename):
		return PageNotExistAnswer().toHTML(request, receiveToken(token) is not None)
	return FileResponse(filename)
