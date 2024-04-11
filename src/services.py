from sqlmodel import SQLModel, create_engine
USER_NAME = "docker"
PASSWORD = "docker"
PORT = "5432"
DB_NAME = "project_planner"
HOST = "localhost"
DATABASE_URL = f'postgresql://{USER_NAME}:{PASSWORD}@{HOST}/{DB_NAME}'



def get_engine():
    return create_engine(DATABASE_URL)
