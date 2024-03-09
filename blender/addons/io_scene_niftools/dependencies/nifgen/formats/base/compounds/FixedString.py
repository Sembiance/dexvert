from nifgen.base_struct import BaseStruct


class FixedString(BaseStruct):

	"""
	Holds a string of a fixed size, given as #ARG#.
	"""

	__name__ = 'FixedString'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = b""

	def __repr__(self):
		return str(self.data)

	@classmethod
	def read_fields(cls, stream, instance):
		instance.data = stream.read(instance.arg)

	@classmethod
	def write_fields(cls, stream, instance):
		stream.write(instance.data)

	@classmethod
	def validate_instance(cls, instance, context, arg=0, template=None):
		super().validate_instance(instance, context, arg, template)
		assert len(instance.data) == arg

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		return len(instance.data)
