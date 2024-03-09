from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class FixedString(BaseStruct):

	__name__ = 'FixedString'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = Array(self.context, 0, None, (0,), name_type_map['Char'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', Array, (0, None, (None,), name_type_map['Char']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', Array, (0, None, (instance.arg,), name_type_map['Char']), (False, None)

	def __new__(cls, context, arg, template=None):
		return "\x00" * arg

	@staticmethod
	def from_stream(stream, context, arg, template=None):
		chars = stream.read(arg)
		return chars.decode(errors="surrogateescape")

	@staticmethod
	def to_stream(instance, stream, context, arg, template=None):
		encoded_instance = instance.encode(errors="surrogateescape")
		assert len(encoded_instance) == arg
		stream.write(encoded_instance)

	@staticmethod
	def get_size(instance, context, arg, template=None):
		return arg

	@classmethod
	def validate_instance(cls, instance, context, arg, template=None):
		assert isinstance(instance, str)
		assert len(instance.encode(errors="surrogateescape")) == arg

	get_field = None
	_get_filtered_attribute_list = None

	@staticmethod
	def from_value(value):
		return str(value)
