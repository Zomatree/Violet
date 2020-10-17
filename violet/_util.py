class IndexableNamespace:
	def __init__(self, **attrs):
		# print(attrs)
		self._vals = []
		for name, value in attrs.items():
			self._vals.append(name)
			setattr(self, name, value)

	def __getitem__(self, idx):
		return getattr(self, self._vals[idx])
