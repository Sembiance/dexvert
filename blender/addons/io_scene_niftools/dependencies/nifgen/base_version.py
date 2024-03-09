class VersionBase:

	def __init__(self, id, supported=True, custom=False, primary_games=(), all_games=(), ext=()):
		self.id = id
		self.supported = supported
		self.custom = custom
		self.primary_games = primary_games
		self.all_games = all_games
		self.ext = (self._file_format, *ext)

	@staticmethod
	def _force_tuple(potential_tuple):
		if isinstance(potential_tuple, (list, tuple)):
			return potential_tuple
		else:
			return (potential_tuple, )

	def __repr__(self):
		return str(self)

	def __str__(self):
		s = f'{type(self).__name__}: id: {self.id}'
		for attr in self._verattrs:
			attr_values = getattr(self, attr)
			if attr_values:
				s += f", {attr}: {attr_values}"
		return s
