class VioletASTBase:
	__slots__ = ()

	def __repr__(self):
		return "{0.__class__.__name__}({1})".format(self, ', '.join(map(repr, (getattr(self, v) for v in self.__slots__))))

class Primitive(VioletASTBase):
	__slots__ = ('type', 'value')

	def __init__(self, type, value):
		self.type = type
		self.value = value

class Identifier(VioletASTBase):
	__slots__ = ('name', 'form')

	def __init__(self, name, form):
		self.name = name
		self.form = form

class TypeId(VioletASTBase):
	__slots__ = ('name',)

	def __init__(self, name):
		self.name = name

class ImportStatement(VioletASTBase):
	__slots__ = ('importing', 'from_module')

	def __init__(self, *importing, from_module):
		self.importing = importing
		self.from_module = from_module

	def __repr__(self):
		return "ImportStatement({0}, from_module={1.from_module!r})".format(', '.join(map(repr, self.importing)), self)

class AssignmentStatement(VioletASTBase):
	__slots__ = ('global_scope', 'constant', 'identifier', 'type', 'expression')

	def __init__(self, scope, constant, identifier, type, expression):
		self.global_scope = scope == 'put'
		self.constant = constant is not None
		self.identifier = identifier
		self.type = type
		self.expression = expression
