import argparse, sys

from violet.lexer import lexer
from violet.parser import parser

parse = argparse.ArgumentParser()
parse.add_argument('file')

if __name__ == '__main__':
	args = parse.parse_args(sys.argv[1:])
	with open(args.file) as f:
		print(parser.parse(lexer.tokenize(f.read())))
