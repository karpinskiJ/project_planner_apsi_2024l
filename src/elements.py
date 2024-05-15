class Element:
	pass
	
class NewLine:

	def __init__(self: Self, element: Element) -> NoneType:
		self.element = element
		
	def contents(self: Self) -> str:
		return self.element.contents() + "<br/>\n"
		
class PlainElement(Element):
	
	def __init__(self: Self, text: str) -> NoneType:
		self.text = text
		
	def contents(self: Self) -> str:
		return self.text
		
class Single:

	def __init__(self: Self, name: str, fields: dict[str, str] = {}, flags: list[str] = [],
		*, internal: Element | NoneType = None, cls: str | NoneType = None) -> NoneType:
		self.fields = fields
		self.flags = flags
		self.internal = internal
		self.cls = cls or self.__class__.cls
		self.newline = newline
		
	def internals(self: Self) -> str:
		return self.internal.contents()
		
	def contents(self: Self, newline: bool = False) -> str:
		result = "<" + name
		fields = copy.copy(self.fields)
		fields['cls'] = self.cls
		for field, value in fields.items():
			result += " " + field + "=\"" + value +"\""
		for flag in self.flags:
			result += " " + flag
		internal = self.internals()
		if not internal:
			result += "/>"
		else:
			result += ">" + internal + "</" + self.name + ">"
		return result

class Label(Single):

	def __init__(self: Self, stub: Stub) -> NoneType:
		super().__init__("label", {}, [], text = stub.text, cls = stub.cls)
			
class Present(Label):
	
	def internals(self: Self):
		return super().internals() + ":&nbsp;"

class Link(Single):

	def __init__(self: Self, element: Element, target: str) -> NoneType:
		super().__init__("a", { "href" : target }, internal = element)
		
class LabelLink(Label):
	
	def __init__(self: Self, stub: Stub, target: str) -> NoneType:
		super().__init__(stub)
		self.link = Link(self, target)
		
	def contents(self: Self) -> str:
		return self.link.contents()
		
class Field:
	
	def __init__(self: Self, key: Label, value: Label):
		self.key = key
		self.value = value
		
	def contents(self: Self):
		return self.key.contents(True) + self.value.contents(True)
		
class Button(Link):

	def __init__(self: Self, stub: Stub, target: str, *, cls: str | NoneType = None):
		super().__init__(Single("button", internal = stub.text, cls = stub.cls), target)
		
