import inspect
from violet.errors import *

# __all__ = ['Module']

_OPS = {
	'plus': '+',
	'minus': '-',
	'times': '*',
	'divide': '/',
	'call': '()'
}

class _Meta(type):
	def __new__(mcs, cname, bases, attrs):
		# print(attrs)
		new = attrs.copy()
		for name, value in attrs.items():
			if name.startswith('_operator_'):
				new.pop(name)
				op = name[10:]
				name = 'operator' + _OPS[op]
				new[name] = value
		return super().__new__(mcs, cname, bases, new)

	def __repr__(cls):
		# return cls.__module__ + '.' + cls.__name__
		return cls.__name__

class Object(metaclass=_Meta):
	def __add__(self, other):
		return self.get_special_method('+')(other)

	def get_special_method(self, name):
		meth = getattr(self, 'operator'+name)
		if meth is None:
			raise OperatorNotApplicable(self, name)
		if not inspect.ismethod(meth):
			raise Panic(f"operator{name} not defined as a callable method")
		return meth

	def __call__(self, args, *, runner):
		return self.get_special_method('()')(args, runner=runner)

class ThinPythonObjectWrapper:
	def __init__(self, obj):
		self.obj = obj

	def __repr__(self):
		return 'PyObject_'+self.obj.__class__.__name__

	def __getattr__(self, name):
		if name == '__repr__':
			return super().__getattribute__(name)
		return self.obj.__getattribute__(name)

	def __str__(self):
		return str(self.obj)

class Module(Object):
	def __init__(self, module):
		self.module = module

	def __repr__(self):
		return f'Module({self.module!r})'

	def __str__(self):
		return repr(self)

	def __getattr__(self, name):
		try:
			return self.module.__getattr__(name)
		except AttributeError:
			raise HasNoAttribute(self, name)

class Primitive(Object):
	def __init__(self, value):
		self.value0 = value

	def get_type(self):
		from violet.vast import TypeId, Identifier
		return TypeId(Identifier(self.__class__.__name__))

	def _operator_plus(self, other):
		# print(self, type(self), self.__qualname__)
		# print(repr(self), repr(other))
		if not isinstance(other, self.__class__):
			raise Exception(f"operator+ not allowed between classes of '{self.__class__.__qualname__}' and '{other.__class__.__name__}'")
		return self.__class__(self.value0 + other.value0)

class Void(Primitive):
	def __init__(self):
		super().__init__(None)

	def __eq__(self, other):
		return isinstance(other, Void)

	def get_type(self):
		from violet.vast import TypeId, Identifier
		return TypeId(Identifier('Void'))

class Boolean(Primitive):
	pass

class String(Primitive):
	@classmethod
	def new(cls, value):
		return cls(str(value))

class Integer(Primitive):
	pass

class List(Primitive):
	@classmethod
	def from_value0(cls, value, runner):
		if not value:  # empty expr list?
			raise Exception("cannot infer type of empty list")
		initial = value[0].eval(runner).__class__
		values = []
		for arg in value:
			arg = arg.eval(runner)
			if not isinstance(arg, initial):
				raise Exception(f"multi-typed lists are invalid (found {arg.__class__.__name__!r}, expected {initial.__name__!r})")
			values.append(arg)
		return cls(values)

class _Break(Exception):
	pass

class Function(Object):
	# _attrs = ('name', 'params', 'return_type', 'body')

	def __init__(self, name, params, return_type, body):
		self.name = name
		self.params = params
		self.return_type = return_type
		self.body = body
		self._return = None

	def _operator_call(self, args, *, runner):
		# print(self.params, args)
		with runner.new_scope():
			if len(args) < len(self.params):
				raise Exception("not enough arguments for function call")
			params = iter(self.params)
			for arg in args:
				value = arg.eval(runner)
				try:
					param = next(params)
				except StopIteration:
					raise Exception("too many arguments for function call") from None
				param.type.type_check(value, runner)
				
				runner.get_current_scope().set_var(param.name, value)
			self._execute(runner)
			# print("returning type", self._return)
			return self._return
	
	def _execute(self, runner):
		for statement in self.body:
			runner.lineno += 1
			# print("executing", statement.__class__.__name__)
			try:
				self._execute_statement(statement, runner)
			except _Break:
				break
			except Exception as e:
				print(f"ERROR:{runner.lineno}: {e}")

	def _execute_statement(self, statement, runner):
		from violet import vast as ast

		if isinstance(statement, ast.AssignmentStatement):
			scope = runner.global_scope if statement.global_scope else runner.get_current_scope()
			expr = statement.expression.eval(runner)
			type = statement.type

			if type is not None:
				type.type_check(expr, runner)

			scope.set_var(statement.identifier, expr, const=statement.constant)

		elif isinstance(statement, ast.ReturnStatement):
			expr = statement.expr
			if expr is None:
				ret = Void()
			else:
				ret = expr.eval(runner)
			if self.return_type is None:
				self.return_type = ret.get_type()
			self.return_type.type_check(ret, runner)
			self._return = ret
			raise _Break

		elif isinstance(statement, ast.FunctionCall):
			statement.eval(runner)

		else:
			raise Exception(f"unexpected statement {statement!r}")
