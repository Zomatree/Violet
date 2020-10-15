from violet.errors import *
from violet import objects
import ast as pyast
from types import BuiltinMethodType as PyMethodType

class VioletASTBase:
	__slots__ = ()
	cls_name = "pp"

	def __repr__(self):
		return "{0.__class__.__name__}({1})".format(self, ', '.join(
			'%s=%r' % (i, getattr(self, i))
			for i in self.__slots__
			if not i.startswith('_')
		))

	def eval(self, runner):
		pass

class Module(VioletASTBase):
	__slots__ = ('body',)
	cls_name = "module"

	def __init__(self, body):
		self.body = body

class Primitive(VioletASTBase):
	__slots__ = ('value', 'type')
	cls_name = "primitive"

	def __init__(self, value, type):
		self.value = value
		self.type = type

	def eval(self, runner):
		if self.type is objects.Void:
			return objects.Void()
		elif self.type is objects.Boolean:
			return self.type(self.value == 'true')
		elif self.type is objects.Integer:
			return self.type(int(self.value))
		elif self.type is objects.String:
			return self.type(pyast.literal_eval(self.value))
		elif self.type is objects.List:
			return self.type.from_value0(self.value, runner=runner)
		else:
			raise Exception(self.type)

class Identifier(VioletASTBase):
	__slots__ = ('name',)
	cls_name = "identifier"

	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		return isinstance(other, self.__class__) and other.name == self.name

	def __hash__(self):
		return self.name.__hash__()

	def transform_to_string(self):
		return self.name

	def get_top_level_name(self):
		return self

	def eval(self, runner):
		return runner.get_current_scope().get_var(self)

class Attribute(Identifier):
	__slots__ = ('name', 'value')
	cls_name = "attribute"

	def __init__(self, name, value):
		super().__init__(name)
		self.value = value

	def transform_to_string(self):
		return self.name.transform_to_string() + '.' + self.value.transform_to_string()

	def get_top_level_name(self):
		return self.name.get_top_level_name()

class Subscript(VioletASTBase):
	__slots__ = ('name', 'index')
	cls_name = "subscript"

	def __init__(self, name, index):
		self.name = name
		self.index = index

class TypeId(VioletASTBase):
	__slots__ = ('name',)

	def __init__(self, name):
		self.name = name

	def type_check(self, value, runner):
		if isinstance(self.name, Subscript):
			supert = self.name.name  # Identifier('List')
			subtypes = self.name.index  # [Identifier('String')]

			typ = runner.get_current_scope().get_var(supert)
			if not isinstance(value, typ):
				raise Exception(f"invalid type {value.__class__.__name__!r} for function call (expected {typ.__name__!r})")
		else:  # single type, eg Identifier('String')
			typ = runner.get_current_scope().get_var(self.name)
			if not isinstance(value, typ):
				raise Exception(f"invalid type {value.__class__.__name__!r} for function call (expected {typ.__name__!r})")

class Import(VioletASTBase):
	__slots__ = ('importing', 'from_module')

	def __init__(self, importing, from_module):
		self.importing = importing
		self.from_module = from_module
		
class Assignment(VioletASTBase):
	__slots__ = ('global_scope', 'constant', 'identifier', 'type', 'expression')

	def __init__(self, scope, constant, identifier, type, expression):
		self.global_scope = scope == 'put'
		self.constant = constant is not None
		self.identifier = identifier
		self.type = type
		self.expression = expression

class Parameter(VioletASTBase):
	__slots__ = ('name', 'type')

	def __init__(self, name, type):
		self.name = name
		self.type = type

class Function(VioletASTBase):
	__slots__ = ('name', 'params', 'ret_value', 'body')

	def __init__(self, name, params, ret_value, body):
		self.name = name
		self.params = params
		self.ret_value = ret_value
		self.body = body

	def eval(self, runner):
		return objects.Function(name, params, ret_value, body)

class FunctionCall(VioletASTBase):
	__slots__ = ('name', 'args')

	def __init__(self, name, args):
		self.name = name
		self.args = args

	def eval(self, runner):
		name = self.name.get_top_level_name()
		obj = runner.get_current_scope().get_var(name)
		attrs = self.name.transform_to_string().split('.')[1:]
		# print(name, obj, attrs)
		for attr in attrs:
			try:
				obj = getattr(obj, attr)
			except AttributeError:
				raise HasNoAttribute(obj, attr)

		args = self.args
		# print(obj, args)

		if isinstance(obj, PyMethodType):
			value = obj(*[o.eval(runner).value0 for o in args])
		else:
			value = obj([o.eval(runner) for o in args], runner=runner)
		# print(value)
		return value

class Return(VioletASTBase):
	__slots__ = 'expr',

	def __init__(self, expr):
		self.expr = expr or objects.Void()

class Control(VioletASTBase):
	def eval(self, runner, func):
		pass

class IfControl(Control):
	__slots__ = 'if_stmt', 'elseif_stmt', 'else_stmt'

	def __init__(self, if_stmt, elseif_stmt=None, else_stmt=None):
		self.if_stmt = if_stmt
		self.elseif_stmt = elseif_stmt
		self.else_stmt = else_stmt

	def eval(self, runner, func):
		can = self.if_stmt.eval(runner, func)
		# print("IF ->", can)
		if not can and self.elseif_stmt:
			can = self.elseif_stmt.eval(runner, func)
			# print("ELSEIF ->", can)
		if not can and self.else_stmt:
			self.else_stmt.eval(runner, func)
			# print("ELSE")

class ForControl(Control):
	pass  # todo

class WhileControl(Control):
	pass  # todo

class LoopControl(Control):
	pass  # todo

class SwitchControl(Control):
	pass  # todo

class If(Control):
	__slots__ = 'expr', 'body'

	def __init__(self, expr, body):
		self.expr = expr
		self.body = body

	def eval(self, runner, func):
		expr = self.expr.eval(runner)
		# print(self.__class__.__name__, "->", self.expr)
		if not isinstance(expr, objects.Boolean):
			raise TypeCheckerFailed(expr, objects.Boolean)
		if expr:
			with runner.new_scope():
				runner.exec_function_body(self.body, func)
		return expr

class ElseIf(Control):
	__slots__ = 'expr', 'body'

	def __init__(self, expr, body):
		self.expr = expr
		self.body = body

	def eval(self, runner, func):
		return If.eval(self, runner, func)

class Else(Control):
	__slots__ = 'body',

	def __init__(self, body):
		self.body = body

	def eval(self, runner, func):
		with runner.new_scope():
			runner.exec_function_body(self.body, func)

class Operator:
	__slots__ = ()

	def __repr__(self):
		return '{0.__class__.__name__}()'.format(self)

# math

class Plus(Operator):
	pass

class Minus(Operator):
	pass

class Times(Operator):
	pass

class Divide(Operator):
	pass

class Modulus(Operator):
	pass

# equality

class EqualTo(Operator):
	pass

class NotEqualTo(Operator):
	pass

class GreaterThan(Operator):
	pass

class GreaterOrEqual(Operator):
	pass

class LessThan(Operator):
	pass

class LessOrEqual(Operator):
	pass

class BiOperatorExpr(VioletASTBase):
	__slots__ = ('left', 'op', 'right')

	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right

	def _Plus(self, l, r):
		return l + r

	def _Minus(self, l, r):
		return l - r

	def _Times(self, l, r):
		return l * r

	def _Divide(self, l, r):
		return l / r

	def _Modulus(self, l, r):
		return l % r

	def _EqualTo(self, l, r):
		return l == r

	def _NotEqualTo(self, l, r):
		return l != r

	def _GreaterThan(self, l , r):
		return l > r

	def _GreaterOrEqual(self, l, r):
		return l >= r

	def _LessThan(self, l, r):
		return l < r

	def _LessOrEqual(self, l, r):
		return l <= r

	def eval(self, runner):
		left = runner.get_var(self.left) if isinstance(self.left, Identifier) else self.left.eval(runner)
		right = runner.get_var(self.right) if isinstance(self.right, Identifier) else self.right.eval(runner)
		# print(left, self.op, right)

		return getattr(self, '_' + self.op.__class__.__name__)(left, right)
		# print(ret)
