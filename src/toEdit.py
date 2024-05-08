class ToEdit:

	def __init__(self, name, label, value = None, typee = "text"):
		self.name = name
		self.label = label
		self.value = value
		self.type = typee
		
	@staticmethod
	def toEdit(kind, model = None, advanced = None):
		from models import (AdvancedUser, ShortUser,
			FullUser, Project, Resource)
		if kind == "user":
			if model:
				if advanced:
					return AdvancedUser.toEdit(model)
				else:
					return ShortUser.toEdit(model)
			else:
				return FullUser.toEdit(model)
		elif kind == "project":
			return Project.toEdit(model)
		elif kind == "resource":
			return Resource.toEdit(model)
