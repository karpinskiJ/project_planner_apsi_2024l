import json

import inputModels as inpute
from fastapi import FastAPI, Request, Form, Path, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
import datetime
import os
from look import *
from edit import edited
from wraps import User, Project, Resource
import wraps
from globs import app, authHandler
from myToken import *
from types import NoneType
import empty
from visitors import ToEditVisitor
import sqlmodel
from services import *
import sqlModels as sql
import sys
from fastapi.responses import StreamingResponse
import csv
import io
from typing import Annotated, Optional
from sqlModels import ProjectRole
from collections import defaultdict
from datetime import datetime, timedelta

@app.get('/', response_class=Response)
def main(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> Response:
    if receiveToken(token):
        return RedirectResponse('/dashboard?kind=user')
    return Answer('main.html', "Welcome").toHTML(request, False)


@app.get('/login', response_class=HTMLResponse)
def login(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    if receiveToken(token):
        return AlreadyLoggedInAnswer().toHTML(request)
    return ToLoginAnswer(ToEditVisitor.visitLogin()).toHTML(request)


@app.get('/register', response_class=HTMLResponse)
def register(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    if receiveToken(token):
        return AlreadyLoggedInAnswer().toHTML(request)
    return ToEditAnswer("user", empty.User().acceptVisitor(ToEditVisitor)).toHTML(request, False)


@app.get('/delete', response_class=HTMLResponse)
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
    delete = SuccessDeleteAnswer(kind, item).toHTML(request, not (kind == "user" and user == wrap))
    if kind == "user" and user == wrap:
        delete.delete_cookie("token")
    return delete


@app.get('/create', response_class=HTMLResponse)
def create(request: Request, kind: Annotated[str | NoneType, Query()] = None,
           token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    if not (kind == "project" or kind == "resource" or kind == "user"):
        return PageNotExistAnswer().toHTML(request)
    if not User(user).canEdit(kind):
        return CannotCreateAnswer(kind)
    return ToEditAnswer(kind, empty.Model.make(kind).acceptVisitor(ToEditVisitor)).toHTML(request)


@app.get('/changePassword', response_class=HTMLResponse)
def changePassword(request: Request,
                   token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    return ToEditAnswer("user", ToEditVisitor.visitChangePassword(),
                        user, passwords=True).toHTML(request)


@app.post('/changedPassword', response_class=HTMLResponse)
def changedPassword(request: Request, old: Annotated[str | NoneType, Form()] = None,
                    password: Annotated[str | NoneType, Form()] = None,
                    repeated: Annotated[str | NoneType, Form()] = None,
                    token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    if not (old and password and repeated):
        return LackOfFieldsAnswer("password", user).toHTML(request)
    if not authHandler.verify(old, User(user).model.password):
        return BadPasswordAnswer().toHTML(request)
    if password != repeated:
        return NotConsistentAnswer("passwords").toHTML(request)
    User(user).password = authHandler.hash(password)
    return SuccessAnswer("Successfully changed password").toHTML(request)


@app.get('/add-project/execute', response_class=HTMLResponse)
def add_project_panel(project, user, allocation, request: Request,
                      token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    print(project)
    print(user)
    with sqlmodel.Session(get_engine()) as session:
        project_id = session.query(sql.Projects).where(sql.Projects.name == project).first().id
        user_id = session.query(sql.Users).where(sql.Users.login == user).first().id
        query = f"""
        Insert into projects_to_resources_lkp (project_id, user_id,allocation_part) values ({project_id}, {user_id},{float(allocation) / 100})
        """

        session.exec(query)
    return RedirectResponse('/lookOne?kind=project&item=' + project)


@app.get('/add-project')
def add_project(project: str, request: Request,
                token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)

    with sqlmodel.Session(get_engine()) as session:
        manager_id = session.query(sql.Users).where(sql.Users.login == user).first().id
        user_workers = session.query(sql.Users).where(sql.Users.manager_id == manager_id).all()

        user_workers = list([user.login for user in user_workers])

        project_id = session.query(sql.Projects).where(sql.Projects.name == project).first().id

    response = templates.TemplateResponse('addToProjectPanel.html'
                                          , {'request': request,
                                             'project_id': project_id,
                                             'project_name': project,
                                             'workers': user_workers
                                             }
                                          )
    return response


@app.get('/add-resource')
def add_project(project: str, request: Request,
                token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)

    with sqlmodel.Session(get_engine()) as session:
        manager_id = session.query(sql.Users).where(sql.Users.login == user).first().id
        user_resources = session.query(sql.TechnicalResources).where(
            sql.TechnicalResources.manager_id == manager_id).all()

        user_resources = list([resource.name for resource in user_resources])

        project_id = session.query(sql.Projects).where(sql.Projects.name == project).first().id

    response = templates.TemplateResponse('addToProjectPanelResource.html'
                                          , {'request': request,
                                             'project_id': project_id,
                                             'project_name': project,
                                             'workers': user_resources
                                             }
                                          )
    return response


@app.get('/add-resource/execute', response_class=HTMLResponse)
def add_project_panel(project, user, allocation, request: Request,
                      token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    with sqlmodel.Session(get_engine()) as session:
        project_id = session.query(sql.Projects).where(sql.Projects.name == project).first().id
        user_id = session.query(sql.TechnicalResources).where(sql.TechnicalResources.name == user).first().id
        query = f"""
        Insert into projects_to_resources_lkp (project_id, resource_id,allocation_part) values ({project_id}, {user_id},{float(allocation) / 100})
        """
        session.exec(query)
    return RedirectResponse('/lookOne?kind=project&item=' + project)


@app.get('/edit', response_class=HTMLResponse)
def edit(request: Request, kind: Annotated[str | NoneType, Query()] = None,
         item: Annotated[str | NoneType, Query()] = None,
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
    if not user.canEdit(kind, wrap):
        return CannotChangeAnswer(kind, item).toHTML(request)
    return ToEditAnswer(kind, wrap.acceptVisitor(ToEditVisitor), item).toHTML(request)


# to change
@app.get('/compose', response_class=HTMLResponse)
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


@app.post('/user', response_class=HTMLResponse)
def user(request: Request, login: Annotated[str | NoneType, Form()] = None,
         name: Annotated[str | NoneType, Form()] = None,
         surname: Annotated[str | NoneType, Form()] = None,
         manager: Annotated[str | NoneType, Form()] = None,
         item: Annotated[str | NoneType, Query()] = None,
         token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = receiveToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    user = User(user)
    if item is None and not user.canEditUser():
        return CannotCreateAnswer("user").toHTML(request)
    print(manager)
    inputModel = inpute.User([login, name, surname], manager=manager, password="password")
    if inputModel is None:
        print("Lack of fields")
        return LackOfFieldsAnswer("user", item).toHTML(request)
    if item is not None and not user.canEditUser(wraps.User(item)):
        print("Cannot change")
        return CannotChangeAnswer("user", item).toHTML(request)
    print("To edited")
    sys.stdout.flush()
    return edited("user", inputModel, item, user).toHTML(request)


@app.post('/project', response_class=HTMLResponse)
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
    user = User(user)
    if item is None and not user.canEditProject():
        return CannotCreateAnswer("project").toHTML(request)
    inputModel = inpute.Project([name, description, datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                 datetime.datetime.strptime(end_date, "%Y-%m-%d"), status, user.id])
    if inputModel is None:
        return LackOfFieldsAnswer("project", item).toHTML(request)
    if item is not None and not user.canEditProject(wraps.Project(item)):
        return CannotChangeAnswer("project", item).toHTML(request)
    if item is None:
        inputModel.owner = user
    return edited("project", inputModel, item, user).toHTML(request)


@app.post('/resource', response_class=HTMLResponse)
def resource(request: Request, name: Annotated[str | NoneType, Form()] = None,
			 type: Annotated[str | NoneType, Form()] = None,
             item: Annotated[str | NoneType, Query()] = None,
             token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    user = User(user)
    if item is None and not user.canEditResource():
        return CannotCreateAnswer("resource").toHTML(request)
    inputModel = inpute.Resource([name, user.id, type])
    if inputModel is None:
        return LackOfFieldsAnswer("resource", item).toHTML(request)
    if item is not None and not user.canEditResource(wraps.Resource(item)):
        return CannotChangeAnswer("resource", item).toHTML(request)
    return edited("resource", inputModel, item).toHTML(request)


@app.post('/logged', response_class=Response)
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
    response.set_cookie(key="token", value=authHandler.encodeToken(login))
    response.status_code = 302
    return response


@app.get('/join', response_class=Response)
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
        if user.inProject(wrap):
            return AlreadyInProjectAnswer(name).toHTML(request)
        elif user.canJoinProject(wrap):
            user.addProject(wrap)
        else:
            return CannotJoinProjectAnswer(name).toHTML(request)
    else:
        if wrap.owner == user:
            return RedirectResponse('/delete?kind=project&item=' + name)
        if not user.inProject(wrap):
            return NotInProjectAnswer(name).toHTML(request)
        else:
            user.releaseProject(wrap)
    return RedirectResponse('/dashboard?kind=project')


@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request, kind: Annotated[str | NoneType, Query()] = None,
              token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)

    if isinstance(user, Answer):
        return user.toHTML(request)
    if kind == "user":
        return lookOneInternal("user", True, user).toHTML(request)
    elif kind == "project":
        return lookInternal("project", "user", True, user).toHTML(request)


@app.get('/calendar-manager-view', response_class=HTMLResponse)
def dashboard(request: Request, kind: Annotated[str | NoneType, Query()] = None,
              token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    with sqlmodel.Session(get_engine()) as session:

        user_data = session.query(sql.Users).where(sql.Users.login == user).first()
        print(user_data.role)

        if user_data.role == ProjectRole.worker:
            user_id = user_data.id
            query_people = f"""
                   SELECT users.login, projects.name, projects_to_resources_lkp.allocation_part, projects.start_date, projects.end_date, projects.description
                     FROM users 
                        INNER JOIN projects_to_resources_lkp ON users.id = projects_to_resources_lkp.user_id
                        INNER join projects on projects_to_resources_lkp.project_id = projects.id
                    WHERE users.id = '{user_id}'
                    """

            data_people = session.exec(query_people).all()
            data_stuff = []
        elif user_data.role == ProjectRole.manager:

            manager_id = session.query(sql.Users).where(sql.Users.login == user).first().id

            query_people = f"""
                       SELECT users.login, projects.name, projects_to_resources_lkp.allocation_part, projects.start_date, projects.end_date, projects.description
                         FROM users 
                            INNER JOIN projects_to_resources_lkp ON users.id = projects_to_resources_lkp.user_id
                            INNER join projects on projects_to_resources_lkp.project_id = projects.id
                        WHERE users.manager_id = '{manager_id}'
            """
            query_stuff = f"""
                       SELECT technical_resources.name, projects.name, projects_to_resources_lkp.allocation_part, projects.start_date, projects.end_date, projects.description
                         FROM  technical_resources
                         INNER JOIN projects_to_resources_lkp ON technical_resources.id = projects_to_resources_lkp.resource_id 
                            INNER join projects on projects_to_resources_lkp.project_id = projects.id
                        WHERE technical_resources.manager_id = '{manager_id}'
            """
            data_people = session.exec(query_people).all()
            data_stuff = session.exec(query_stuff).all()
        else:
            query_people = f"""
                       SELECT users.login, projects.name, projects_to_resources_lkp.allocation_part, projects.start_date, projects.end_date, projects.description
                         FROM users 
                            INNER JOIN projects_to_resources_lkp ON users.id = projects_to_resources_lkp.user_id
                            INNER join projects on projects_to_resources_lkp.project_id = projects.id
                        
            """
            query_stuff = f"""
                       SELECT technical_resources.name, projects.name, projects_to_resources_lkp.allocation_part, projects.start_date, projects.end_date, projects.description
                         FROM  technical_resources
                         INNER JOIN projects_to_resources_lkp ON technical_resources.id = projects_to_resources_lkp.resource_id 
                            INNER join projects on projects_to_resources_lkp.project_id = projects.id
                        
            """

            data_people = session.exec(query_people).all()
            data_stuff = session.exec(query_stuff).all()
    data = data_people + data_stuff
    employess = list(set([row[0] for row in data]))
    output = [{"user": employee, "assignments": []} for employee in employess]
    for row in data:
        for employee in output:
            if employee['user'] == row[0]:
                employee['assignments'].append(
                    {"project": row[1], "start": row[3].isoformat(), "end": row[4].isoformat(), "info": row[5],
                     "allocation_part": f"{row[2] * 100}%   "})

    response = templates.TemplateResponse('calendar_board.html'
                                          , {'request': request,
                                             'projects': json.dumps(output)
                                             }
                                          )
    return response


@app.get('/lookOne', response_class=HTMLResponse)
def lookOne(request: Request, kind: Annotated[str | NoneType, Query()] = None,
            item: Annotated[str | NoneType, Query()] = None,
            token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    return lookOneInternal(kind, item, user).toHTML(request)


@app.get('/look', response_class=HTMLResponse)
def look(request: Request, kind: Annotated[str | NoneType, Query()] = None,
         of: Annotated[str | NoneType, Query()] = None,
         item: Annotated[str | NoneType, Query()] = None,
         token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    return lookInternal(kind, of, item, user).toHTML(request)


@app.get('/logout', response_class=Response)
def logout(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> Response:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    response = RedirectResponse('/')
    response.delete_cookie("token")
    return response


@app.get('/advanced', response_class=HTMLResponse)
def advanced(request: Request, token: Annotated[str | NoneType, Cookie()] = None) -> HTMLResponse:
    user = checkToken(token)
    if isinstance(user, Answer):
        return user.toHTML(request)
    return Answer("advanced.html", "Advanced").toHTML(request)


@app.get('/{resource}', response_class=Response)
def getResource(request: Request, resource: Annotated[str, Path()],
                token: Annotated[str | NoneType, Cookie()] = None) -> Response:
    filename = "templates/" + resource
    if not os.path.isfile(filename):
        return PageNotExistAnswer().toHTML(request, receiveToken(token) is not None)
    return FileResponse(filename)


@app.get("/download/projects")
def download_projects(token: Annotated[str | NoneType, Cookie()] = None):
    output = io.StringIO()
    writer = csv.writer(output)
    user = checkToken(token)
    with sqlmodel.Session(get_engine()) as session:
        user_role = session.query(sql.Users).where(sql.Users.login == user).first().role
        print(user_role)
        if user_role ==ProjectRole.admin:
            query = f"""
                    SELECT users.login, projects.name, projects.start_date, projects.end_date, projects.description, projects.status
                         FROM users 
                            INNER JOIN projects_to_resources_lkp ON users.id = projects_to_resources_lkp.user_id
                            INNER join projects on projects_to_resources_lkp.project_id = projects.id
            """
            data = session.exec(query).all()
            columns = ["User_name","Project_name", "start_date", "end_date", " Project_description","status"]
            writer.writerow(columns)
            for row in data:
                writer.writerow(row)
            response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=admin_projects_report.csv"
            return response
        elif user_role ==ProjectRole.manager:
            manager_id = session.query(sql.Users).where(sql.Users.login == user).first().id

            query = f"""
                       SELECT users.login, projects.name, projects.start_date, projects.end_date, projects.description, projects.status
                         FROM users 
                            INNER JOIN projects_to_resources_lkp ON users.id = projects_to_resources_lkp.user_id
                            INNER join projects on projects_to_resources_lkp.project_id = projects.id
                        WHERE users.manager_id = '{manager_id}'
            """
            data = session.exec(query).all()
            columns = ["User_name","Project_name", "start_date", "end_date", " Project_description","status"]
            writer.writerow(columns)
            for row in data:
                writer.writerow(row)
            response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=manager_projects_report.csv"
            return response
        elif user_role ==ProjectRole.worker:
            worker_id = session.query(sql.Users).where(sql.Users.login == user).first().id
            query = f"""
                SELECT projects.start_date, projects.end_date, projects_to_resources_lkp.allocation_part, 
                    projects.name, projects.description, projects.status
                    FROM users 
                        INNER JOIN projects_to_resources_lkp ON users.id = projects_to_resources_lkp.user_id
                        INNER JOIN projects ON projects_to_resources_lkp.project_id = projects.id
                    WHERE projects_to_resources_lkp.user_id = '{worker_id}'
            """
            data = session.exec(query).all()

            date_allocation = defaultdict(lambda: {'allocation': 0.0, 'projects': []})

            for row in data:
                start_date = row['start_date']
                end_date = row['end_date']
                allocation = float(row['allocation_part'])
                project_info = {
                    'name': row['name'],
                    'description': row['description'],
                    'status': row['status']
                }
                current_date = start_date
                while current_date <= end_date:
                    date_allocation[current_date]['allocation'] += allocation
                    date_allocation[current_date]['projects'].append(project_info)
                    current_date += timedelta(days=1)

            output = io.StringIO()
            columns = ['Date', 'Allocation', 'Project Names', 'Project Descriptions', 'Project Statuses']
            writer = csv.writer(output)
            writer.writerow(columns)
            for date in sorted(date_allocation.keys()):
                row = date_allocation[date]
                project_names = "; ".join([proj['name'] for proj in row['projects']])
                project_descriptions = "; ".join([proj['description'] for proj in row['projects']])
                project_statuses = "; ".join([proj['status'] for proj in row['projects']])
                writer.writerow([date.strftime('%Y-%m-%d'), row['allocation'], project_names, project_descriptions, project_statuses])

            response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=worker_projects_report.csv"
            return response
        else:
            return f"User role: {user_role} is not allowed!"


@app.get("/download/users")
def download_users(token: Optional[str] = Cookie(None)):
    output = io.StringIO()
    writer = csv.writer(output)
    with sqlmodel.Session(get_engine()) as session:
        query = f"""
                   SELECT id,name,surname,role,setup_time FROM users
        """
        data = session.exec(query).all()
    columns = ["User_id", " User_name", "User_surname", "User_role", "setup_time"]
    writer.writerow(columns)
    for row in data:
        writer.writerow(row)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=users_report.csv"
    return response
