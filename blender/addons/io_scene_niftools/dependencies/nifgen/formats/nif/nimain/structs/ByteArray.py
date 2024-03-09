from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class ByteArray(BaseStruct):

	"""
	An array of bytes.
	"""

	__name__ = 'ByteArray'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The number of bytes in this array
		self.data_size = name_type_map['Uint'](self.context, 0, None)

		# The bytes which make up the array
		self.data = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'data', Array, (0, None, (instance.data_size,), name_type_map['Byte']), (False, None)

	def __new__(self, context=None, arg=0, template=None, set_default=True):
		data_size = name_type_map["Uint"](context, 0, None)
		return b'\x00' * data_size

	@staticmethod
	def from_stream(stream, context=None, arg=0, template=None):
		data_size = name_type_map["Uint"].from_stream(stream)
		return stream.read(data_size)

	@staticmethod
	def to_stream(instance, stream, context, arg=0, template=None):
		data_size = len(instance)
		name_type_map["Uint"].to_stream(data_size, stream, context, 0, None)
		stream.write(instance)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		data_size = len(instance)
		return name_type_map["Uint"].get_size(data_size, context, 0, None) + data_size

	get_field = None
	_get_filtered_attribute_list = None

	@staticmethod
	def fmt_member(instance, indent=0):
		return repr(instance)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		data_size = len(instance)
		name_type_map["Uint"].validate_instance(data_size, context, 0, None)
		assert isinstance(instance, (bytes, bytearray)), f'{instance} is not a byte or bytearray'
