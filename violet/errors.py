class Panic(BaseException):
	pass	

class StatementError(Exception):
	def __init__(self, stmt, msg):
		super().__init__(msg)
		self.stmt = stmt