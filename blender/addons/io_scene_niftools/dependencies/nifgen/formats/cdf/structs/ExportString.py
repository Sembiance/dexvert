from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.cdf.imports import name_type_map


class ExportString(BaseStruct):

	"""
	Sized strings in CDF header ending with 00.
	"""

	__name__ = 'ExportString'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The string length.
		self.length = name_type_map['Littleuint32'](self.context, 0, None)

		# The string itself, null terminated (the null terminator is taken into account in the length uint).
		self.value = Array(self.context, 0, None, (0,), name_type_map['Char'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Littleuint32'], (0, None), (False, None), (None, None)
		yield 'value', Array, (0, None, (None,), name_type_map['Char']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Littleuint32'], (0, None), (False, None)
		yield 'value', Array, (0, None, (instance.length,), name_type_map['Char']), (False, None)

	def __new__(self, context, arg=0, template=None, set_default=True):
		return ''

	@staticmethod
	def from_stream(stream, context=None, arg=0, template=None):
		length = Littleuint32.from_stream(stream)
		chars = stream.read(length)[:-1]
		return chars.decode(errors="surrogateescape")

	@staticmethod
	def to_stream(instance, stream, context, arg=0, template=None):
		instance = instance + '\x00'
		encoded_instance = instance.encode(errors="surrogateescape")
		length = len(encoded_instance)
		Littleuint32.to_stream(length, stream, context)
		stream.write(encoded_instance)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		string_len = len(instance.encode(errors="surrogateescape")) + 1
		return Littleuint32.get_size(string_len, context) + string_len

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert isinstance(instance, str)
		Littleuint32.validate_instance(len((instance + '\x00').encode(errors="surrogateescape")), context)

	get_field = None
	_get_filtered_attribute_list = None

	@staticmethod
	def from_value(value):
		return str(value)

