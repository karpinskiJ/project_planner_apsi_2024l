from sqlmodel import Field, SQLModel
from datetime import datetime, date
from typing import Optional


class Projects(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str = Field(max_length=100)
    description: str
    start_date: date
    end_date: date
    status: str


class Users(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    login: str = Field(max_length=50)
    password: str = Field(max_length=50)
    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    role: str = Field(max_length=50)
    project_id: int


class TechnicalResources(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str = Field(max_length=100)
    project_id: int
