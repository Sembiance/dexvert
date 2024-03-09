from nifgen.formats.cdf.imports import name_type_map
from nifgen.formats.cdf.structs.Header import Header

class CdfFile(Header):

	def __init__(self, context=None, arg=0, template=None, set_default=True):
		if context is None:
			context = self
		super().__init__(context, arg, template, set_default)

	@classmethod
	def from_path(cls, path):
		with open(path, "rb") as stream:
			instance = cls.from_stream(stream, None)
			return instance

	@classmethod
	def to_path(cls, instance, path):
		with open(path, "wb") as stream:
			cls.to_stream(instance, stream, instance.context, instance.arg, instance.template)