from typing import Self
from types import NoneType

class Button:
	# May represent buttons and hyperlinks
	# is used for custom actions in look (as button)
	# is used for listing things in look (as hyperlink)
	# LinkVisitor uses it

	def __init__(self: Self, text: str, link: str) -> NoneType:
		self.text = text
		self.link = link
		
class Label:
	# Represents usual captions in lookOne
	# is used by LookOneVisitor

	def __init__(self: Self, label: str, text: str) -> NoneType:
		self.label = label
		self.text = text

class Link:
	# There is only one place
	# ( in function lookOneInternal )
	# where it is used
	# represents custom dependencies

	def __init__(self: Self, label: str, text: str, link: str) -> NoneType:
		self.label = label
		self.text = text
		self.link = link
		
class ToEdit:
	# used by ToEditVisitor
	# for generating text input fields

	def __init__(self: Self, name: str, label: str,
		value: str | NoneType = None, typee: str = "text") -> NoneType:
		self.name = name
		self.label = label
		self.value = value
		self.type = typee
