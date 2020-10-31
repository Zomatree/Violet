import argparse, glob, sys
import io
from contextlib import redirect_stdout as rout, redirect_stderr as rerr
import traceback

from violet.runner import Runner

parse = argparse.ArgumentParser()
parse.add_argument('file', nargs='?')
parse.add_argument('-v', '--verbose', action='store_true')
parse.add_argument('--test', action='store_true')

if __name__ == '__main__':
	args = parse.parse_args(sys.argv[1:])

	if not args.test:
		Runner.open(args.file, debug=args.verbose).run()
	else:
		failed = False
		for file in glob.glob("examples/*.vi"):
			print("\nTEST:", file)
			try:
				Runner.open(file, debug=args.verbose).run()
			except SystemExit:
				failed = True
			except BaseException:
				traceback.print_exc(file=sys.stderr)
				failed = True
			# print(out.getvalue())
		if failed:
			print("\n\n-- TESTS FAILED --")
		else:
			print("\n\n-- TESTS PASSED --")
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