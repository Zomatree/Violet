import argparse, sys

from violet.runner import Runner

parse = argparse.ArgumentParser()
parse.add_argument('file')

if __name__ == '__main__':
	args = parse.parse_args(sys.argv[1:])
	Runner.open(args.file).run()
	"""
	with open(args.file) as f:
		mod = Module([])
		parser = get_parser()
		output = parser.parse(lexer.tokenize(f.read()))
		if not output:
			for tok in parser._error_list:
				# print("Unexpected token", repr(tok.value), "on line", tok.lineno)
			sys.exit(1)
		mod.body.extend(output)
		# print(mod)
	"""