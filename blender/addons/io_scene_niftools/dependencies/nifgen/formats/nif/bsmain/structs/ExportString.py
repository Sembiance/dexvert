import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class ExportString(BaseStruct):

	"""
	Specific to Bethesda-specific header export strings.
	"""

	__name__ = 'ExportString'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The string length.
		self.length = name_type_map['Byte'](self.context, 0, None)

		# The string itself, null terminated (the null terminator is taken into account in the length byte).
		self.value = Array(self.context, 0, None, (0,), name_type_map['Char'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'value', Array, (0, None, (None,), name_type_map['Char']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Byte'], (0, None), (False, None)
		yield 'value', Array, (0, None, (instance.length,), name_type_map['Char']), (False, None)

	def __new__(self, context, arg=0, template=None, set_default=True):
		return ''

	@staticmethod
	def from_stream(stream, context=None, arg=0, template=None):
		length = name_type_map["Byte"].from_stream(stream)
		chars = stream.read(length)[:-1]
		return NifFormat.safe_decode(chars)

	@staticmethod
	def to_stream(instance, stream, context, arg=0, template=None):
		instance = instance + '\x00'
		encoded_instance = NifFormat.encode(instance)
		length = len(encoded_instance)
		name_type_map["Byte"].to_stream(length, stream, context)
		stream.write(encoded_instance)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		string_len = len(NifFormat.encode(instance)) + 1
		return name_type_map["Byte"].get_size(string_len, context) + string_len

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert isinstance(instance, str), f'{instance} is not a string'
		name_type_map["Byte"].validate_instance(len(NifFormat.encode(instance + '\x00')), context)

	get_field = None
	_get_filtered_attribute_list = None

	@staticmethod
	def from_value(value):
		return str(value)

