from sqlmodel import Field, SQLModel, Column
from datetime import datetime, date
from typing import Optional, Self, Any
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM


class ProjectRole(Enum):
    manager = 'manager'
    worker = 'worker'
    admin = 'admin'


class ResourceType(Enum):
    it_equipment = 'it_equipment'
    vehicle = 'vehicle'
    office_equipment = 'office_equipment'
    other = 'other'


class ProjectStatus(Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'


class Projects(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str = Field(max_length=100)
    status: ProjectStatus = Column(ENUM(ProjectStatus))
    description: str
    start_date: date
    end_date: date
    owner_id: int

    def __getattr__(self: Self, attr: str) -> Any:
        if attr == "uniqueName":
            return self.login
        raise AttributeError(attr, self.__class__)

    def acceptVisitor(self: Self, visitor: Any) -> Any:
        return visitor.visitProject(self)


class Users(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    login: str = Field(max_length=50)
    password: str = Field(max_length=200)
    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    role: ProjectRole = Column(ENUM(ProjectRole))
    manager_id: Optional[int]
    setup_time: datetime

    def __getattr__(self: Self, attr: str) -> Any:
        if attr == "uniqueName":
            return self.login
        raise AttributeError(attr, self.__class__)

    def acceptVisitor(self: Self, visitor: Any) -> Any:
        return visitor.visitUser(self)


class TechnicalResources(SQLModel, table=True):
    __tablename__ = "technical_resources"
    id: Optional[int] = Field(primary_key=True)
    manager_id: int
    name: str = Field(max_length=100)
    type: ResourceType = Column(ENUM(ResourceType))

    def __getattr__(self: Self, attr: str) -> Any:
        if attr == "uniqueName":
            return self.name
        raise AttributeError(attr, self.__class__)

    def acceptVisitor(self: Self, visitor: Any) -> Any:
        return visitor.visitResource(self)


class ProjectResources(SQLModel, table=True):
    __tablename__ = "project_resources"
    id: Optional[int] = Field(primary_key=True)
    project_id: int
    resource_id: int
    allocation_part: float


class ProjectsToResourcesLkp(SQLModel, table=True):
    __tablename__ = "projects_to_resources_lkp"
    id: Optional[int] = Field(primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    user_id: int = Field(foreign_key="users.id")
    resource_id: int = Field(foreign_key="technical_resources.id")
    allocation_part: float

