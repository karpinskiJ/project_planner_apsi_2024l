class ErrorResponse:
	
	def __new__(cls, message, templates, request):
		return templates.TemplateResponse('message.html', { "title" : "Sorry", 
			"message" : message, "request" : request})
			
class SuccessResponse:
	
	def __new__(cls, message, templates, request):
		return templates.TemplateResponse('message.html', { "title" : "Got it", 
			"message" : message, "request" : request})

class EmptyResponse:

	def __new__(cls, title, templates, request):
		return templates.TemplateResponse('empty.html', { "title" : title,
			"request" : request })
