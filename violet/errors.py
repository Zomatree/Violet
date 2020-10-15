class BaseError:
	def __init__(self, message):
		self.message = message

	def __repr__(self):
		return f'{self.__class__.__name__}({self.message!r})'

	def __str__(self):
		return self.message

class HasNoAttribute(BaseError, Exception):
	def __init__(self, obj, name):
		super().__init__(f"{obj.__name__!r} has no attribute {name!r}")

class TypeCheckerFailed(BaseError, Exception):
	def __init__(self, unexpected, expected):
		super().__init__(f"unexpected type {unexpected.__class__.__name__!r} (expected {expected.__name__!r})")

class ModuleDoesNotExist(BaseError):
	def __init__(self, name):
		super().__init__(f'module {name!r} does not exist')

class FailedToImportFromModule(BaseError):
	def __init__(self, name, module):
		super().__init__(f'failed to import {name!r} from {module!r}')

class OperatorNotApplicable(BaseError, Exception):
	def __init__(self, obj, op):
		super().__init__(f'operator {op!r} not applicable on {obj!r}')

class Panic(BaseException):
	pass	
