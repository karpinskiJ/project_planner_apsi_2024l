from sqlmodel import SQLModel, create_engine
USER_NAME = "docker"
PASSWORD = "docker"
PORT = "5432"
DB_NAME = "project_planner"
HOST = "localhost"
DATABASE_URL = f'postgresql://{USER_NAME}:{PASSWORD}@{HOST}/{DB_NAME}'



def get_engine():
	# I do not known the return value type
	engine = create_engine(DATABASE_URL)
	print("Engine: ", type(engine))
	return engine
