import contextlib
import hashlib
import importlib
import re
import os
import pprint
import sys
import types
import contextlib

from violet.lexer import lexer
from violet.parser import parser
from violet import vast as ast
from violet import errors
from violet import objects

_STD_TYPES = {
	'nil': objects.Void,
	'List': objects.List,
	'String': objects.String,
	'Void': objects.Void,
	'Integer': objects.Integer,
	'Boolean': objects.Boolean
}

_PY_TYPES = {
	int: objects.Integer,
	str: objects.String,
	type(None): objects.Void,
	list: objects.List.from_value0
}

_print = print
def print(*args, **kwargs):
	kwargs['file'] = kwargs.get('file', sys.stderr)
	_print(*args, **kwargs)

class VarNotFound(Exception):
	def __init__(self, var):
		super().__init__(f"variable {var.name!r} is not defined")

class CannotReassignConst(Exception):
	def __init__(self, var):
		super().__init__(f"constant variable {var.name!r} cannot be reassigned")

class Scope:
	def __init__(self):
		self.vars = {}
		self.const_vars = {}
		self.parent = None

		self.hash = hashlib.sha1(os.urandom(16)).hexdigest()
		# print("spawned scope", self.hash)

	def __repr__(self):
		return "Scope(" + repr(self.vars) + ", " + repr(self.const_vars) + ")"

	def is_var_assigned(self, identifier):
		return identifier in self.vars or identifier in self.const_vars or identifier.name in _STD_TYPES

	def get_var_noid(self, name):
		return self.get_var(ast.Identifier(name))

	def get_var(self, identifier):
		# print(self.hash, ": getting", identifier)
		try:
			if identifier.name in _STD_TYPES:
				return _STD_TYPES[identifier.name]
			var = self.vars.get(identifier)
			if var is None:
				var = self.const_vars.get(identifier)
			if var is None:
				raise VarNotFound(identifier)
			return var
		except VarNotFound:
			if not self.parent:  # self.parent?.getVar(identifier) ?: throw error
				raise
			return self.parent.get_var(identifier)

	def reassign_var(self, identifier, value):
		if identifier in self.const_vars:
			raise CannotReassignConst(identifier)  # cannot reassign consts
		orig = self.vars[identifier]
		if not orig.type_check(value):
			raise errors.TypeCheckerFailed(value, orig.__class__)
		self.vars[identifier] = value

	def set_var(self, identifier, value, *, const=False):
		# print(self.hash, ": assigning", identifier, value)
		if not isinstance(value, objects.Object):
			value = objects.ThinPythonObjectWrapper(value)
		# print("assigning", identifier, "to", value, "as const?", const)
		if self.is_var_assigned(identifier):
			# print(identifier, "already assigned")
			return self.reassign_var(identifier, value)
		if const:
			# print("set const var")
			self.const_vars[identifier] = value
		else:
			# print("set var")
			self.vars[identifier] = value

class Runner:
	def __init__(self, code):
		self.global_scope = gl = Scope()
		self.scopes = {gl.hash: gl}
		self.active_scope = gl.hash
		self.code = code
		self.runtime_errors = []
		self.lineno = 0

	@staticmethod
	def wrap_py_type(value):
		return _PY_TYPES[type(value)](value, runner=self)

	def get_var(self, *args, **kwargs):
		return self.get_current_scope().get_var(*args, **kwargs)

	def get_current_scope(self):
		return self.scopes[self.active_scope]

	@classmethod
	def open(cls, fp):
		with open(fp) as f:
			return cls(f.read())

	def run(self):
		module = ast.Module([])
		body = parser.parse(lexer.tokenize(self.code))
		if parser._error_list:
			for error in parser._error_list:
				pass
				print(f"ERROR:{error.lineno}: Unexpected {error.value!r}")
			sys.exit(1)

		module.body.extend(body)
		# print(module, file=sys.stdout)
		try:
			# print(module.body)
			self.exec_module(module)
		except errors.Panic as e:
			print("FATAL: system error occured:", e, file=sys.stderr)
			sys.exit(9)
		# print(self.get_current_scope())
		# pprint.pprint(self.scopes)
		# return self
		# print(module, file=sys.stdout)
		try:
			main = self.get_current_scope().get_var(ast.Identifier('main'))
		except VarNotFound:
			print("ERROR: missing entry point function 'main'", file=sys.stderr)
			sys.exit(1)

		argv = ast.Primitive([
			ast.Primitive('"a"', type=objects.String),
			# ast.Primitive('1', type=objects.Integer)
		], type=objects.List).eval(self)

		try:
			main([argv], runner=self)
		except Exception as e:
			# raise e
			print(f"ERROR:{self.lineno}", e, file=sys.stderr)
			sys.exit(1)

		# pprint.pprint(self.scopes)

	@contextlib.contextmanager
	def new_scope(self):
		scope = Scope()
		scope.parent = self.get_current_scope()
		self.scopes[scope.hash] = scope
		old_scope = self.active_scope
		# print("opening scope", scope.hash, "with parent", old_scope)
		self.active_scope = scope.hash
		try:
			yield
		finally:
			# print("closing scope", scope.hash, "to", old_scope)
			self.active_scope = old_scope

	def exec_module_body(self, stmt_list):
		for statement in stmt_list:
			self.lineno += 1
			# print("executing", statement)

			if isinstance(statement, ast.Import):
				self._exec_import(statement)
			elif isinstance(statement, ast.Assignment):
				self._exec_assignment(statement)
			elif isinstance(statement, ast.Function):
				self._exec_function_spawn(statement)
			else:
				print(f"ERROR:{self.lineno}: unexpected {statement.__class__.__name__!r} statement", file=sys.stderr)

			for error in self.runtime_errors:
				print(f"ERROR:{self.lineno}: {error}", file=sys.stderr)
			self.runtime_errors.clear()

	def exec_function_body(self, body, func):
		for statement in body:
			if func._return_flag:
				break
			self.lineno += 1
			# print("executing", statement.__class__.__name__)
			if isinstance(statement, ast.Assignment):
				self._exec_assignment(statement)
			elif isinstance(statement, ast.Return):
				self._exec_return(statement, func)
				func._return_flag = True
			elif isinstance(statement, ast.FunctionCall):
				statement.eval(self)
			elif isinstance(statement, ast.Control):
				statement.eval(self, func)
			else:
				print(f"ERROR:{self.lineno}: unexpected {statement.__class__.__name__!r} statement", file=sys.stderr)

	def exec_module(self, module):
		self.exec_module_body(module.body)

	def _exec_import(self, stmt):
		form = stmt.from_module
		if isinstance(form, ast.Attribute):
			if form.name.name == 'std':
				return self._exec_std_import(stmt)
		else:
			if form.name == 'std':
				return self._exec_std_import(stmt)
			return self._exec_local_import(stmt)

	def _exec_std_import(self, stmt):
		# print(stmt)
		form = stmt.from_module
		name = form.transform_to_string()

		try:
			# print("importing violet."+name)
			module = importlib.import_module('violet.'+name)
		except ImportError:
			# print("import failed")
			self.runtime_errors.append(errors.ModuleDoesNotExist(name))
		else:
			for iport in stmt.importing:
				if not hasattr(module, iport.name):
					# print("failed to import", iport)
					self.runtime_errors.append(errors.FailedToImportFromModule(iport.name, name))
				else:
					# print("imported", iport)
					self.get_current_scope().set_var(iport, getattr(module, iport.name))
		# print(self.get_current_scope())

	def _exec_local_import(self, stmt):
		try:
			new = Runner.open(stmt.from_module.name+'.vi').run()
		except FileNotFoundError:
			self.runtime_errors.append(errors.ModuleDoesNotExist(stmt.from_module.name))
			return

		for name in stmt.importing:
			try:
				var = new.get_current_scope().get_var(name)
			except Exception as e:
				self.runtime_errors.append(errors.FailedToImportFromModule(name.name, stmt.from_module.name))
				# print(type(e).__name__, e)
			else:
				self.get_current_scope().set_var(name, var)

	def _exec_assignment(self, statement):
		# print(statement)
		scope = self.global_scope if statement.global_scope else self.get_current_scope()
		expr = statement.expression.eval(self)
		# print(expr)
		typ = statement.type

		if typ is not None:
			typ.type_check(expr, self)

		try:
			scope.set_var(statement.identifier, expr, const=statement.constant)
		except Exception as e:
			# raise e
			self.runtime_errors.append(str(e))

	def _exec_return(self, statement, func):
		# print(statement)
		expr = statement.expr
		if expr is None:
			ret = Void()
		else:
			ret = expr.eval(self)
		if func.return_type is None:
			if not isinstance(ret, objects.Object):
				ret = self.wrap_py_type(ret)
			func.return_type = ret.get_type()
		func.return_type.type_check(ret, self)
		func._return = ret

	def _exec_function_spawn(self, stmt):
		# print("spawn function")
		self.get_current_scope().set_var(stmt.name, objects.Function(stmt.name, stmt.params, stmt.ret_value, stmt.body))
	