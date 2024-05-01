from fastapi.middleware.cors import CORSMiddleware
import models
from services import *
from sqlmodel import Session, select
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, Path, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from typing import Annotated
from auth import AuthHandler
from responses import ErrorResponse, SuccessResponse, EmptyResponse

app = FastAPI()
allowed_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="./templates")

authHandler = AuthHandler()
	
@app.get('/', response_class=HTMLResponse)
def main(request: Request):
	return templates.TemplateResponse('main.html', {'request': request})

@app.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})
    
@app.get('/register', response_class=HTMLResponse)
def register(request: Request):
	return templates.TemplateResponse('register.html', {'request': request})
	
@app.post('/registered', response_class=HTMLResponse)
def registered(request: Request, username: Annotated[str, Form()], 
	password: Annotated[str, Form()], repeatedPassword: Annotated[str, Form()],
	name: Annotated[str, Form()], surname: Annotated[str, Form()],
	role: Annotated[str, Form()]):
	with Session(get_engine()) as session:
		if session.exec(select(models.Users).where(models.Users.login == username)).first():
			return ErrorResponse("Such user already exists", templates, request)
	if password != repeatedPassword:
		return ErrorResponse("Passwords do not fit", templates, request)
	with Session(get_engine()) as session:
		session.add(models.Users(login = username, password = authHandler.hash(password), 
		name = name, surname = surname, role = role))
		session.commit()
	return SuccessResponse("You successfully registered", templates, request)

@app.post('/logged')
def logged(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]):
	with Session(get_engine()) as session:
		correctPassword = session.exec(select(models.Users.password).
			where(models.Users.login == username)).first()
		print(correctPassword)
		if not correctPassword:
			return ErrorResponse("There is no such user", templates, request)
		if not authHandler.verify(password, correctPassword):
			return ErrorResponse('Bad password', templates, request)
	response = RedirectResponse("/dashboard?kind=user")
	response.set_cookie(key = "token", value = authHandler.encodeToken(username))
	response.status_code = 302
	return response
	
@app.get('/dashboard')
def dashboard(request: Request, kind: Annotated[str, Query()],
	token: Annotated[str, Cookie()] = None):
	if not token:
		return ErrorResponse("You have no token", templates, request)
	decoded = authHandler.decodeToken(token)
	if decoded == AuthHandler.expired:
		return ErrorResponse("Your token expired", templates, request)
	if decoded == AuthHandler.invalid:
		return ErrorResponse("Invalid token", templates, request)
	with Session(get_engine()) as session:
		user = session.exec(select(models.Users).
			where(models.Users.login == decoded)).first()
		if kind == "user":
			return templates.TemplateResponse('user_dashboard.html',
				{ "identifier" : user.id, "login" : decoded,
				"name" : user.name, "surname" : user.surname,
				"role" : user.role, "request": request})
		if kind == "projects":
			project = session.exec(select(models.Projects).
				where(models.Projects.id == user.project_id)).first()
			if not project:
				return EmptyResponse("Dashboard", templates, request)
			return templates.TemplateResponse('project_dashboard.html',
				{ "identifier" : project.id, "name": project.name,
				"description" : project.description, "startDate" : project.start_date,
				"endDate" : project.end_date, "status" : project.status, "request": request })
		
@app.get('/{resource}')
def getStyle(resource: Annotated[str, Path()]):
	return FileResponse("templates/" + resource)
