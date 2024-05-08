from passlib.context import CryptContext
from datetime import datetime
import jwt

class AuthHandler:
	#security = HTTPBearer()
	context = CryptContext(schemes=['bcrypt'], deprecated='auto')
	secret = 'SECRET'
	
	expired = 0
	invalid = 1
	
	def hash(self, password):
		return self.context.hash(password)
		
	def verify(self, plainPassword, hashedPassword):
		return self.context.verify(plainPassword, hashedPassword)
		
	def encodeToken(self, login):
		return jwt.encode(
			{
			"iat" : datetime.utcnow(),
			"sub" : login
			},
			self.secret,
			algorithm = "HS256"
			)
			
	def decodeToken(self, token):
		try:
			return jwt.decode(token, self.secret, algorithms = ['HS256'])['sub']
		except jwt.ExpiredSignatureError:
			return AuthHandler.expired
		except jwt.InvalidTokenError:
			return AuthHandler.invalid
	
