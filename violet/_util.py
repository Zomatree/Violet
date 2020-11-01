class IndexableNamespace:
	def __init__(self, **attrs):
		# print(attrs)
		self._vals = []
		for name, value in attrs.items():
			self._vals.append(name)
			setattr(self, name, value)

	def __getitem__(self, idx):
		return getattr(self, self._vals[idx])

from functools import wraps

def identify_as_violet():
	def outer(func):
		func._0_identifies_as_violet = 1
		return func
	return outer
