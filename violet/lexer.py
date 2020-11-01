import sys
from sly import Lexer

class VioletLexer(Lexer):
	tokens = {
		CAST,

		LAMBDA_SEP,

		PLUS,
		MINUS,
		MULTIPLY,
		DIVIDE,
		MODULUS,

		EQ,
		NE,
		GE,
		GT,
		LE,
		LT,

		EOS,
		EQUALS,
		COLON,
		DQMARK,
		QMARK,

		BLOCK_OPEN,
		BLOCK_CLOSE,
		PAREN_OPEN,
		PAREN_CLOSE,
		BRACK_OPEN,
		BRACK_CLOSE,

		ATTR,
		COMMA,

		IDENTIFIER,

		SCOPE,

		IMPORT,
		FROM,
		CONST,
		FUN,
		RETURN,

		TRUE,
		FALSE,
		NIL,

		IF,
		ELSEIF,
		ELSE,

		DECIMAL,
		STRING,
	}
	ignore_comment = r"//.*"

	CAST = '->'

	LAMBDA_SEP = r"=>"

	PLUS = r'\+'
	MINUS = r'-'
	MULTIPLY = r'\*'
	DIVIDE = r'/'
	MODULUS = '%'

	EQ = '=='
	NE = '!='
	GE = '>='
	GT = '>'
	LE = '<='
	LT = '<'

	EOS = ';'
	EQUALS = '='
	COLON = ':'
	DQMARK = r'\?\?'
	QMARK = r'\?'

	BLOCK_OPEN = '{'
	BLOCK_CLOSE = '}'
	PAREN_OPEN = r'\('
	PAREN_CLOSE = r'\)'
	BRACK_OPEN = r'\['
	BRACK_CLOSE = r'\]'

	ATTR = r'\.'
	COMMA = ','

	IDENTIFIER = r'[a-zA-Z_]+'

	IDENTIFIER['let'] = SCOPE
	IDENTIFIER['put'] = SCOPE

	IDENTIFIER['import'] = IMPORT
	IDENTIFIER['from'] = FROM
	IDENTIFIER['const'] = CONST
	IDENTIFIER['fun'] = FUN
	IDENTIFIER['return'] = RETURN

	IDENTIFIER['true'] = TRUE
	IDENTIFIER['false'] = FALSE
	IDENTIFIER['nil'] = NIL

	IDENTIFIER['if'] = IF
	IDENTIFIER['elseif'] = ELSEIF
	IDENTIFIER['else'] = ELSE

	# BINARY = r'0b[01]+'
	DECIMAL = r'[0-9]+'
	# HEXADECIMAL = r'0x[0-9a-fA-F]+'

	STRING = r'".*?(?<!\\)(?:\\\\)*?"'

	ignore = ' \t'

	ignore_newline = r'\n+'
	def ignore_newline(self, t):
		self.lineno += t.value.count('\n')

	def error(self, t):
		print(f"ERROR:{self.lineno}: Illegal character {t.value[0]!r}")
		# self.errok()
		sys.exit(1)

lexer = VioletLexer()
