import sqlmodel
from services import get_engine
from types import NoneType
from typing import Self, Any

class Query:

	def __init__(self: Self, content, multiple: bool = False) -> NoneType:
		self.content = content
		self.multiple = multiple
		
class AbstractSession:
	pass

class Session(AbstractSession):

	def __init__(self: Self, general: "General") -> NoneType:
		super().__init__()
		self.generals = [ general ]
		self.session = sqlmodel.Session(get_engine())
		
	def __call__(self: Self, query: Query) -> Any:
		result = self.session.exec(query.content)
		return result.all() if query.multiple else result.first()
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "toSession":
			return self
		raise AttributeError(attr, self.__class__)
		
	def addGeneral(self: Self, general: "General") -> NoneType:
		self.generals.append(general)
		
	def close(self: Self) -> NoneType:
		self.session.close()
		for general in self.generals:
			general.session = None
			
	def add(self: Self, row: sqlmodel.SQLModel, *, toDelete: bool = False) -> NoneType:
		if toDelete:
			self.session.delete(row)
		else:
			self.session.add(row)
		self.session.commit()


class ProxySession(AbstractSession):
	
	def __init__(self: Self, general: "General", session: Session) -> NoneType:
		self.session = session.toSession
		self.session.addGeneral(general)
		
	def __call__(self: Self, query: Query) -> Any:
		return self.session(query)
		
	def __getattr__(self: Self, attr: str) -> Any:
		if attr == "toSession":
			return self.session
		raise AttributeError(attr, self.__class__)
		
	def add(self: Self, row: sqlmodel.SQLModel, *, toDelete: bool = False) -> NoneType:
		self.session.add(row, toDelete = toDelete)
		
	def close(self: Self) -> NoneType:
		pass
