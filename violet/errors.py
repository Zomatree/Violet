class Panic(BaseException):
	pass	

class StatementError(Exception):
	def __init__(self, stmt, msg):
		super().__init__(msg)
		self.stmt = stmt

class _Exit(Exception):
	pass

class ReturnExit(_Exit):
	pass

class BreakExit(_Exit):
	pass

class ContinueExit(_Exit):
	pass
