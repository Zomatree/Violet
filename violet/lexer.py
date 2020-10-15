import sys
from sly import Lexer

class VioletLexer(Lexer):
	tokens = {
		PLUS,
		MINUS,
		MULTIPLY,
		DIVIDE,
		EOS,
		EQUALS,
		COLON,
		BLOCK_OPEN,
		BLOCK_CLOSE,
		PAREN_OPEN,
		PAREN_CLOSE,
		ATTR,
		COMMA,
		BRACK_OPEN,
		BRACK_CLOSE,

		IMPORT,
		FROM,
		SCOPE,
		CONST,
		FUN,
		RETURN,
		TRUE,
		FALSE,
		NIL,

		IDENTIFIER,
		NUMBER,
		STRING,
	}

	PLUS = r'\+'
	MINUS = r'-'
	MULTIPLY = r'\*'
	DIVIDE = r'/'
	EOS = ';'
	EQUALS = '='
	COLON = ':'
	BLOCK_OPEN = '{'
	BLOCK_CLOSE = '}'
	PAREN_OPEN = r'\('
	PAREN_CLOSE = r'\)'
	ATTR = r'\.'
	COMMA = ','
	BRACK_OPEN = r'\['
	BRACK_CLOSE = r'\]'

	IDENTIFIER = r'[a-zA-Z_]+'
	IDENTIFIER['import'] = IMPORT
	IDENTIFIER['from'] = FROM
	IDENTIFIER['let'] = SCOPE
	IDENTIFIER['put'] = SCOPE
	IDENTIFIER['const'] = CONST
	IDENTIFIER['fun'] = FUN
	IDENTIFIER['return'] = RETURN
	IDENTIFIER['true'] = TRUE
	IDENTIFIER['false'] = FALSE
	IDENTIFIER['nil'] = NIL

	NUMBER = r'[0-9]+'
	STRING = r'".*?(?<!\\)(?:\\\\)*?"'

	ignore = ' \t'

	ignore_newline = r'\n+'
	def ignore_newline(self, t):
		self.lineno += t.value.count('\n')

	def error(self, t):
		print(f"ERROR:{self.lineno}: Illegal character {t.value[0]!r}")
		sys.exit(1)

lexer = VioletLexer()
