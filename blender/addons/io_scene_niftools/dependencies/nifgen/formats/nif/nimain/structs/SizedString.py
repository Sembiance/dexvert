import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class SizedString(BaseStruct):

	"""
	A string of given length.
	"""

	__name__ = 'SizedString'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The string length.
		self.length = name_type_map['Uint'](self.context, 0, None)

		# The string itself.
		self.value = Array(self.context, 0, None, (0,), name_type_map['Char'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'value', Array, (0, None, (None,), name_type_map['Char']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Uint'], (0, None), (False, None)
		yield 'value', Array, (0, None, (instance.length,), name_type_map['Char']), (False, None)

	def __new__(self, context=None, arg=0, template=None, set_default=True):
		return ''

	@staticmethod
	def from_stream(stream, context=None, arg=0, template=None):
		length = name_type_map["Uint"].from_stream(stream)
		chars = stream.read(length)
		return NifFormat.safe_decode(chars)

	@staticmethod
	def to_stream(instance, stream, context, arg=0, template=None):
		encoded_instance = NifFormat.encode(instance)
		name_type_map["Uint"].to_stream(len(encoded_instance), stream, context)
		stream.write(encoded_instance)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		string_len = len(NifFormat.encode(instance))
		return name_type_map["Uint"].get_size(string_len, context) + string_len

	get_field = None
	_get_filtered_attribute_list = None

	@staticmethod
	def fmt_member(instance, indent=0):
		return repr(instance)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert isinstance(instance, str), f'{instance} is not a string'
		assert len(NifFormat.encode(instance)) <= 4294967295

	@staticmethod
	def from_value(value):
		return str(value)

