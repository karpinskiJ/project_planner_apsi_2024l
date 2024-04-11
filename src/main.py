from fastapi.middleware.cors import CORSMiddleware
import models
from services import *
from sqlmodel import Session
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, Path
from fastapi.responses import HTMLResponse, RedirectResponse, Response


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


# Login route
@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@app.get('/hello-world')
def hello_world(request: Request):
    with Session(get_engine()) as session:
        all_projects = session.query(models.Projects).all()
        return {"projects": all_projects}
