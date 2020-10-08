import typing

from sly import Parser

from violet.lexer import VioletLexer
from . import vast as ast

def getanyattr(obj, *names):
	for name in names:
		o = getattr(obj, name, ...)
		if o is not ...:
			return o

class VioletParser(Parser):
	debugfile = 'parsetab.out'
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
		pass

	@_("expr EOS")
	@_("iport EOS")
	@_("assign EOS")
	@_("func_call EOS")
	@_("func")
	def stmt(self, p):
		# print("STATEMENT")
		pass

	@_("SCOPE identity EQUALS expr")
	@_("SCOPE CONST identity EQUALS expr")
	def assign(self, p):
		stmt = ast.AssignmentStatement(p.SCOPE, getanyattr(p, 'CONST'), p.identity, None, p.expr)
		print(stmt)
		return stmt

	@_("SCOPE identity COLON typ EQUALS expr")
	@_("SCOPE CONST identity COLON typ EQUALS expr")
	def assign(self, p):
		stmt = ast.AssignmentStatement(p.SCOPE, getanyattr(p, 'CONST'), p.identity, p.typ, p.expr)
		print(stmt)
		return stmt

	# expressions

	@_("expr PLUS expr")
	def expr(self, p):
		return p.expr0 + p.expr1

	@_("expr MINUS expr")
	def expr(self, p):
		return p.expr0 - p.expr1

	@_("expr MULTIPLY expr")
	def expr(self, p):
		return p.expr0 * p.expr1

	@_("expr DIVIDE expr")
	def expr(self, p):
		return p.expr0 / p.expr1

	@_("identity")
	def expr(self, p):
		print("identify", p.identity)
		return p.identity

	@_("identity ATTR IDENTIFIER")
	@_("IDENTIFIER")
	def identity(self, p):
		# print("attr ident", p.IDENTIFIER)
		return ast.Identifier(p.IDENTIFIER, getanyattr(p, 'identity'))

	@_("primitive")
	def expr(self, p):
		return p.primitive

	@_('NUMBER')
	def primitive(self, p):
		prim = ast.Primitive(ast.Identifier("Integer", None), int(p.NUMBER))
		print(prim)
		return prim

	@_('STRING')
	def primitive(self, p):
		prim = ast.Primitive(ast.Identifier("String", None), p.STRING[1:-1])
		print(prim)
		return prim

	# import

	@_("identifier_list COMMA identity")
	@_("identity")
	def identifier_list(self, p):
		idlist = getanyattr(p, 'identifier_list')
		if idlist:
			ret = (*idlist, p.identity)
		else:
			ret = (p.identity,)
		print(ret)
		return ret

	@_("IMPORT BLOCK_OPEN identifier_list BLOCK_CLOSE")
	def iport(self, p):
		imp = ast.ImportStatement(*p.identifier_list, from_module=None)
		print(imp)
		return imp

	@_("IMPORT BLOCK_OPEN identifier_list BLOCK_CLOSE FROM IDENTIFIER")
	def iport(self, p):
		imp = ast.ImportStatement(*p.identifier_list, from_module=p.IDENTIFIER)
		print(imp)
		return imp

	# types

	@_("identity BRACK_OPEN identifier_list BRACK_CLOSE")
	@_("identity")
	def typ(self, p):
		idlist = getanyattr(p, 'identifier_list')
		# print("typ", p.IDENTIFIER, idlist)
		if idlist is not None:
			if len(idlist) == 1:
				ret = ast.TypeId(idlist[0])
			else:
				ret = ast.TypeId(tuple(idlist))
		else:
			ret = ast.TypeId(p.identity)
		print(ret)
		return ret

	# functions

	@_("identity COLON typ EQUALS expr")
	@_("identity COLON typ")
	def param(self, p):
		print("param", p.identity, p.typ)

	@_("param_list COMMA param")
	@_("param")
	def param_list(self, p):
		l = getanyattr(p, 'param_list')
		if l is not None:
			print("param_list", l, p.param)
		else:
			print("param_list", p.param)

	@_("BLOCK_OPEN stmt_list BLOCK_CLOSE")
	def block(self, p):
		print("opened new block")
		pass

	@_("FUN identity PAREN_OPEN param_list PAREN_CLOSE block")
	@_("FUN identity PAREN_OPEN param_list PAREN_CLOSE COLON typ block")
	def func(self, p):
		has_ending_type = getanyattr(p, 'IDENTIFIER0') is not None
		if has_ending_type:
			print("fun", p.identity0, "(", p.param_list, "):", p.identity1)
		else:
			print("fun", p.identity, "(", p.param_list, ")")

	# function calls

	@_("arg_list COMMA expr")
	@_("expr")
	def arg_list(self, p):
		print("arg_list", p.expr)

	@_("identity PAREN_OPEN PAREN_CLOSE")
	@_("identity PAREN_OPEN arg_list PAREN_CLOSE")
	def func_call(self, p):
		print("call", p.identity)

	def error(self, t):
		if not t:
			print("ERROR:-1: EOF encountered")
		else:
			print(f"ERROR:{t.lineno}: Unexpected {t.value!r}")

parser = VioletParser()
