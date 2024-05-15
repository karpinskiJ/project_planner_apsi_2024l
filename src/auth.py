from passlib.context import CryptContext
from datetime import datetime
from typing import Self
import jwt

class AuthHandler:
	#security = HTTPBearer()
	context = CryptContext(schemes=['bcrypt'], deprecated='auto')
	secret = 'SECRET'
	
	expired = 0
	invalid = 1
	
	def hash(self: Self, password: str) -> str:
		return self.context.hash(password)
		
	def verify(self: Self, plainPassword: str, hashedPassword: str) -> bool:
		return self.context.verify(plainPassword, hashedPassword)
		
	def encodeToken(self: Self, login: str) -> str:
		return jwt.encode(
			{
			"iat" : datetime.utcnow(),
			"sub" : login
			},
			self.secret,
			algorithm = "HS256"
			)
			
	def decodeToken(self: Self, token: str) -> int | str:
		try:
			return jwt.decode(token, self.secret, algorithms = ['HS256'])['sub']
		except jwt.ExpiredSignatureError:
			return AuthHandler.expired
		except jwt.InvalidTokenError:
			return AuthHandler.invalid
	
