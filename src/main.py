import inputModels as inpute
from fastapi import FastAPI, Request, Form, Path, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from typing import Annotated
import datetime
import os
from answers import *
from look import *
from edit import edited
import inputModels as inpute
from wraps import User, Project, Resource
import wraps
from globs import app, authHandler
from myToken import *
from types import NoneType
import empty
from visitors import ToEditVisitor
	
@app.get('/', response_class = Response)
def main(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> Response:
	if receiveToken(token):
		return RedirectResponse('/dashboard?kind=user')
	return Answer('main.html', "Welcome").toHTML(request, False)

@app.get('/login', response_class = HTMLResponse)
def login(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	if receiveToken(token):
		return AlreadyLoggedInAnswer().toHTML(request)
	return ToLoginAnswer(ToEditVisitor.visitLogin()).toHTML(request)
    
@app.get('/register', response_class = HTMLResponse)
def register(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	if receiveToken(token):
		return AlreadyLoggedInAnswer().toHTML(request)
	return ToEditAnswer("user", empty.User().acceptVisitor(ToEditVisitor)).toHTML(request, False)

@app.post('/delete', response_class = HTMLResponse)
@app.get('/delete', response_class = HTMLResponse)
def delete(request: Request, kind: Annotated[str | NoneType, Query()] = None,
	item: Annotated[str | NoneType, Query()] = None, 
	password: Annotated[str | NoneType, Form()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind is None:
		return PageNotExistAnswer().toHTML(request)
	if item is None:
		if kind != "user":
			return PageNotExistAnswer().toHTML(request)
		else:
			item = user
	wrap = General.make(kind, item)
	if not wrap.exists:
		return ItemNotExistsAnswer(kind, item).toHTML(request)
	user = User(user)
	if kind == "user":
		if not user.canDeleteUser(wrap):
			return CannotDeleteAnswer("user", item).toHTML(request)
	else:
		if not user.canEdit(kind, wrap):
			return CannotDeleteAnswer(kind, item).toHTML(request)
	if kind == "user" and user == wrap:
		if password is None:
			return (CommitAnswer(ToEditVisitor.visitCommit(), "/delete?kind=user&item=" + item)
				.toHTML(request))
		elif not authHandler.verify(password, wrap.model.password):
			return BadPasswordAnswer().toHTML(request)
	wrap.delete()
	delete = SuccessDeleteAnswer(kind, item).toHTML(request, not(kind == "user" and user == wrap) )
	if kind == "user" and user == wrap:
		delete.delete_cookie("token")
	return delete

@app.get('/promote', response_class = HTMLResponse)
def promote(request: Request, item: Annotated[str | NoneType, Query()] = None,
	promote: Annotated[bool, Query()] = True,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	user = User(user)
	if item is None:
		return PageNotExistAnswer().toHTML(request)
	wrap = User(item)
	if not wrap.exists:
		return ItemNotExistsAnswer("kind", item).toHTML(request)
	if promote:
		if user.admin and not wrap.admin:
			wrap.makeAdmin(user)
			return SuccessPromoteAnswer(item).toHTML(request)
		else:
			return CannotPromoteAnswer(item).toHTML(request)
	else:
		if user.admin and wrap.inherits(user):
			wrap.degrade()
			return SuccessDegradeAnswer(item).toHTML(request)
		else:
			return CannotDegradeAnswer(item).toHTML(request)
	
@app.get('/create', response_class = HTMLResponse)
def create(request: Request, kind: Annotated[str | NoneType, Query()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind != "project" and kind != "resource":
		return PageNotExistAnswer().toHTML(request)
	if not User(user).canEdit(kind):
		return CannotCreateAnswer(kind)
	return ToEditAnswer(empty.Model.make(kind).acceptVisitor(ToEditVisitor)).toHTML(request)

@app.get('/edit', response_class = HTMLResponse)
def edit(request: Request, kind: Annotated[str | NoneType, Query()] = None,
	item: Annotated[str | NoneType, Query()] = None,
	advanced: Annotated[bool, Query()] = False,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind == "user" and item is None:
		item = user
	if kind != "project" and kind != "resource" and kind != "user" or item is None:
		return PageNotExistAnswer().toHTML(request)
	user = User(user)
	wrap = General.make(kind, item)
	if not wrap.exists:
		return ItemNotExistsAnswer(kind, item).toHTML(request)
	if kind == "user":
		if user != wrap:
			return CannotChangeAnswer("user", item).toHTML(request)
	else:
		if not user.canEdit(kind, wrap):
			return CannotChangeAnswer(kind, item).toHTML(request)
	return ToEditAnswer(kind, wrap.acceptVisitor(ToEditVisitor,
		advanced = advanced), item, advanced = advanced).toHTML(request)

@app.get('/compose', response_class = HTMLResponse)
def compose(request: Request, item: Annotated[str, Query()] = None,
	compose: Annotated[bool, Query()] = True,
	token: Annotated[str, Cookie()] = None):
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	user = User(user)
	wrap = Resource(item)
	if not wrap.exists:
		return ItemNotExistsAnswer("resource", item).toHTML(request)
	if not user.owns:
		return CannotChangeAnswer("resource", item).toHTML(request)
	if compose:
		if wrap.project:
			return CannotChangeAnswer("resource", item).toHTML(request)
		wrap.project = user.project
		return SuccessAnswer("Successfully added resource").toHTML(request)
	else:
		if user.project != wrap.project:
			return CannotChangeAnswer("resource", item).toHTML(request)
		wrap.project = None
		return SuccessAnswer("Successfully released resource").toHTML(request)
	
	
@app.post('/user', response_class = HTMLResponse)
def user(request: Request, login: Annotated[str | NoneType, Form()] = None, 
	password: Annotated[str | NoneType, Form()] = None,
	repeated: Annotated[str | NoneType, Form()] = None,
	old: Annotated[str | NoneType, Form()] = None,
	name: Annotated[str | NoneType, Form()] = None, 
	surname: Annotated[str | NoneType, Form()] = None,
	role: Annotated[str | NoneType, Form()] = None,
	advanced: Annotated[bool, Query()] = False,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
		item = receiveToken(token)
		logged = item is not None
		inputModel = inpute.makeUser(logged, advanced, login, password,
			repeated, old, name, surname, role)
		if inputModel is None:
			return LackOfFieldsAnswer("user", item).toHTML(request, logged)
		return edited("user", inputModel, item, User(item)).toHTML(request, logged)
			
@app.post('/project', response_class = HTMLResponse)
def project(request: Request, name: Annotated[str | NoneType, Form()] = None, 
	description: Annotated[str | NoneType, Form()] = None,
	start_date: Annotated[str | NoneType, Form()] = None,
	end_date: Annotated[str | NoneType, Form()] = None,
	status: Annotated[str | NoneType, Form()] = None, 
	item: Annotated[str | NoneType, Query()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse: 
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	inputModel = inpute.Project([name, description, datetime.datetime.strptime(start_date, "%Y-%m-%d"), 
			datetime.datetime.strptime(end_date, "%Y-%m-%d"), status])
	if inputModel is None:
		return LackOfFieldsAnswer("project", item).toHTML(request)
	wrap = wraps.Project(inputModel)
	user = User(user)
	if not user.canEditProject(wrap):
		return CannotChangeAnswer("project", item).toHTML(request)
	if item is None:
		inputModel.owner = user
	return edited("project", inputModel, item, user).toHTML(request)
	
@app.post('/resource', response_class = HTMLResponse)
def resource(request: Request, name: Annotated[str | NoneType, Form()] = None,
	item: Annotated[str | NoneType, Query()] = None, 
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	inputModel = inpute.Resource([name])
	wrap = wraps.Resource(inputModel)
	if inputModel is None:
		return LackOfFieldsAnswer("resource", item).toHTML(request)
	if not User(user).canEditResource(wrap):
		return CannotChangeAnswer("resource", item).toHTML(request)
	return edited("resource", inputModel, item).toHTML(request)
	
	
@app.post('/logged', response_class = Response)
def logged(request: Request, 
	login: Annotated[str | NoneType, Form()] = None,
	password: Annotated[str | NoneType, Form()] = None) -> Response:
	if login is None or password is None:
		return PageNotExistAnswer().toHTML(request, False)
	wrap = User(login)
	if not wrap.exists:
		return ItemNotExistsAnswer("user", login).toHTML(request, False)
	elif not authHandler.verify(password, wrap.model.password):
		return BadPasswordAnswer().toHTML(request, False)
	response = RedirectResponse("/dashboard?kind=user")
	response.set_cookie(key = "token", value = authHandler.encodeToken(login))
	response.status_code = 302
	return response

@app.get('/add', response_class = HTMLResponse)
def add(request: Request, kind: Annotated[str | NoneType, Query()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind != "project" and kind != "resource":
		return PageNotExistAnswer().toHTML(request)
	if not User(user).canEdit(kind):
		return CannotCreateAnswer(kind).toHTML(request)
	model = empty.Project() if kind == "project" else empty.Resource()
	return ToEditAnswer(kind, model.acceptVisitor(ToEditVisitor)).toHTML(request)
	
@app.get('/join', response_class = Response)
def join(request: Request, join: Annotated[bool, Query()] = True,
	name: Annotated[str | NoneType, Query()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> Response:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if name is None:
		return PageNotExistAnswer().toHTML(request)
	user = User(user)
	wrap = Project(name)
	if not wrap.exists:
		return ItemNotExistsAnswer("project", name).toHTML(request)
	if join:
		if user.project == wrap:
			return AlreadyInProjectAnswer(name).toHTML(request)
		elif user.canJoinProject(wrap):
			user.project = wrap
		else:
			return CannotJoinProjectAnswer(name).toHTML(request)
	else:
		if wrap.owner == user:
			return RedirectResponse('/delete?kind=project&item=' + name)
		if wrap != user.project:
			return NotInProjectAnswer(name).toHTML(request)
		else:
			user.project = None
	return RedirectResponse('/dashboard?kind=project')

@app.get('/dashboard', response_class = HTMLResponse)
def dashboard(request: Request, kind: Annotated[str | NoneType, Query()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	if kind == "user":
		return lookOneInternal("user", True, user).toHTML(request)
	elif kind == "project":
		return lookInternal("project", "user", True, user).toHTML(request)

@app.get('/lookOne', response_class = HTMLResponse)
def lookOne(request: Request, kind: Annotated[str | NoneType, Query()] = None,
	item: Annotated[str | NoneType, Query()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	return lookOneInternal(kind, item, user).toHTML(request)

@app.get('/look', response_class = HTMLResponse)
def look(request: Request, kind: Annotated[str | NoneType, Query()] = None,
	of: Annotated[str | NoneType, Query()] = None,
	item: Annotated[str | NoneType, Query()] = None,
	token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	return lookInternal(kind, of, item, user).toHTML(request)

@app.get('/logout', response_class = Response)
def logout(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> Response:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	response = RedirectResponse('/')
	response.delete_cookie("token")
	return response

@app.get('/advanced', response_class = HTMLResponse)
def advanced(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
	user = checkToken(token)
	if isinstance(user, Answer):
		return user.toHTML(request)
	return Answer("advanced.html", "Advanced").toHTML(request)

@app.get('/{resource}', response_class = Response)
def getResource(request: Request, resource: Annotated[str, Path()],
	token: Annotated[str | NoneType, Cookie()] = None) -> Response:
	filename = "templates/" + resource
	if not os.path.isfile(filename):
		return PageNotExistAnswer().toHTML(request, receiveToken(token) is not None)
	return FileResponse(filename)
