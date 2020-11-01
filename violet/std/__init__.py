from sys import stdout
from violet._util import identify_as_violet

__all__ = ['typeof', 'print']

@identify_as_violet()
def typeof(o, **k):
	# pyprint("TYPE TRANSFORM", o)
	l = type(o[0])
	# pyprint(l)
	return l

pyprint = print
@identify_as_violet()
def print(args, *, runner):
	from violet.objects import String
	for arg in args:
		if not isinstance(arg, String):
			raise Exception(f"expected type \"String\", got {arg.__class__.__name__!r}")
		# pyprint("PRINT TRANSFORM", arg)
		# pyprint(repr(arg))
		s = eval(str(arg))
		stdout.write(s)
	stdout.write('\n')
