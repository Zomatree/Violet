import copy
import typing

from sly import Parser

from violet.lexer import VioletLexer
from violet import vast as ast
from violet import objects

def getanyattr(obj, *names):
	for name in names:
		o = getattr(obj, name, ...)
		if o is not ...:
			return o

class VioletParser(Parser):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._error_list = []

	debugfile = None # 'parsetab.out'
	tokens = VioletLexer.tokens

	precedence = (
		('left', DIVIDE, MULTIPLY),
		('left', PLUS, MINUS),
	)

	# statements

	@_("stmt")
	@_("stmt_list stmt")
	def stmt_list(self, p):
		# print("stmt_list")
		orig = getanyattr(p, 'stmt_list')
		if orig:
			return orig + [p.stmt]
		return [p.stmt]

	@_("expr EOS")
	@_("iport EOS")
	@_("assign EOS")
	# @_("func_call EOS")
	@_("func EOS")
	@_("return_stmt EOS")
	def stmt(self, p):
		# print("STATEMENT")
		return getanyattr(p, 'expr', 'iport', 'assign', 'func_call', 'func', 'return_stmt', 'newline')

	@_("SCOPE name EQUALS expr")
	@_("SCOPE CONST name EQUALS expr")
	def assign(self, p):
		stmt = ast.AssignmentStatement(p.SCOPE, getanyattr(p, 'CONST'), p.name, None, p.expr)
		# print(stmt)
		return stmt

	@_("SCOPE name COLON typ EQUALS expr")
	@_("SCOPE CONST name COLON typ EQUALS expr")
	def assign(self, p):
		stmt = ast.AssignmentStatement(p.SCOPE, getanyattr(p, 'CONST'), p.name, p.typ, p.expr)
		# print(stmt)
		return stmt

	# expressions

	@_("expr_list COMMA expr")
	@_("expr")
	def expr_list(self, p):
		if len(p) == 3:
			return [*p.expr_list, p.expr]
		return [p.expr]

	@_("func_call")
	def expr(self, p):
		return p.func_call

	@_("expr PLUS expr")
	def expr(self, p):
		return ast.BiOperatorExpr(p.expr0, ast.Plus(), p.expr1)

	@_("expr MINUS expr")
	def expr(self, p):
		return ast.BiOperatorExpr(p.expr0, ast.Minus(), p.expr1)

	@_("expr MULTIPLY expr")
	def expr(self, p):
		return ast.BiOperatorExpr(p.expr0, ast.Times(), p.expr1)

	@_("expr DIVIDE expr")
	def expr(self, p):
		return ast.BiOperatorExpr(p.expr0, ast.Divide(), p.expr1)

	@_("identity")
	def expr(self, p):
		return p.identity
	"""
	@_("identity ATTR IDENTIFIER")
	@_("IDENTIFIER")
	def identity(self, p):
		# print("attr ident", p.IDENTIFIER)
		return ast.Identifier(p.IDENTIFIER, getanyattr(p, 'identity'))

	"""
	@_("IDENTIFIER")
	def name(self, p):
		return ast.Identifier(p.IDENTIFIER)

	@_("identity ATTR name")
	# @_("name ATTR name")
	@_("name")
	def identity(self, p):
		# print("attr ident", p.IDENTIFIER)
		if len(p) == 3:
			return ast.Attribute(p.identity, p.name)
		return p.name
		
	# """

	@_("primitive")
	def expr(self, p):
		return p.primitive

	@_('NUMBER')
	def primitive(self, p):
		prim = ast.Primitive(p.NUMBER, type=objects.Integer)
		# print(prim)
		return prim

	@_('STRING')
	def primitive(self, p):
		prim = ast.Primitive(p.STRING, type=objects.String)
		# print(prim)
		return prim

	@_('TRUE')
	@_('FALSE')
	def primitive(self, p):
		return ast.Primitive(getanyattr(p, 'TRUE', 'FALSE'), type=objects.Boolean)

	@_('NIL')
	def primitive(self, p):
		return ast.Primitive(p.NIL, type=objects.Void)

	@_('BRACK_OPEN expr_list BRACK_CLOSE')
	@_('BRACK_OPEN BRACK_CLOSE')
	def primitive(self, p):
		return ast.Primitive(getattr(p, 'expr_list', []), type=objects.List)

	# import

	@_("identifier_list COMMA identity")
	@_("identity")
	def identifier_list(self, p):
		idlist = getanyattr(p, 'identifier_list')
		if idlist:
			ret = [*idlist, p.identity]
		else:
			ret = [p.identity,]
		# print(ret)
		return ret

	@_("name_list COMMA name")
	@_("name")
	def name_list(self, p):
		idlist = getanyattr(p, 'name_list')
		if idlist:
			ret = [*idlist, p.name]
		else:
			ret = [p.name,]
		return ret

	@_("IMPORT BLOCK_OPEN name_list BLOCK_CLOSE FROM identity")
	def iport(self, p):
		imp = ast.ImportStatement(p.name_list, from_module=p.identity)
		# print(imp)
		return imp

	# types

	@_("identity BRACK_OPEN identifier_list BRACK_CLOSE")
	@_("identity")
	def typ(self, p):
		idlist = getanyattr(p, 'identifier_list')
		# print("typ", p.IDENTIFIER, idlist)
		if idlist is not None:
			ret = ast.TypeId(ast.Subscript(p.identity, idlist))
		else:
			ret = ast.TypeId(p.identity)
		# print(ret)
		return ret

	# functions

	@_("name COLON typ EQUALS expr")
	@_("name COLON typ")
	def param(self, p):
		return ast.Parameter(p.name, p.typ)

	@_("param_list COMMA param")
	@_("param")
	def param_list(self, p):
		l = getanyattr(p, 'param_list')
		if l is not None:
			return l + [p.param]
		else:
			return [p.param]

	@_("BLOCK_OPEN stmt_list BLOCK_CLOSE")
	@_("BLOCK_OPEN BLOCK_CLOSE")
	def block(self, p):
		return getattr(p, 'stmt_list', [])

	@_("FUN name PAREN_OPEN param_list PAREN_CLOSE block")
	@_("FUN name PAREN_OPEN param_list PAREN_CLOSE COLON typ block")
	@_("FUN name PAREN_OPEN PAREN_CLOSE block")
	@_("FUN name PAREN_OPEN PAREN_CLOSE COLON typ block")
	def func(self, p):
		return ast.Function(p.name, getattr(p, 'param_list', []), getanyattr(p, 'typ'), p.block)

	# function calls

	@_("arg_list COMMA expr")
	@_("expr")
	def arg_list(self, p):
		if len(p) == 3:
			return p.arg_list + [p.expr]
		return [p.expr]

	@_("identity PAREN_OPEN PAREN_CLOSE")
	@_("identity PAREN_OPEN arg_list PAREN_CLOSE")
	def func_call(self, p):
		fun = ast.FunctionCall(p.identity, getattr(p, 'arg_list', []))
		# print(fun)
		return fun

	@_("RETURN expr")
	@_("RETURN")
	def return_stmt(self, p):
		return ast.ReturnStatement(getanyattr(p, 'expr'))

	def error(self, t):
		if not t:
			print("ERROR:-1: EOF encountered")
		else:
			print(f"ERROR:{t.lineno}: unexpected {t.value!r}")
			self._error_list.append(copy.copy(t))

parser = VioletParser()
