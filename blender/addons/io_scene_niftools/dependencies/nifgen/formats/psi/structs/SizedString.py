from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.psi.imports import name_type_map


class SizedString(BaseStruct):

	"""
	A string of given length.
	"""

	__name__ = 'SizedString'


	def __init__(self, context, arg=0, template=None, set_default=True):
		if template is None:
			raise TypeError(f'{type(self).__name__} requires template is not None')
		super().__init__(context, arg, template, set_default=False)

		# The string length.
		self.length = self.template(self.context, 0, None)

		# The string itself.
		self.value = Array(self.context, 0, None, (0,), name_type_map['Char'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', None, (0, None), (False, None), (None, None)
		yield 'value', Array, (0, None, (None,), name_type_map['Char']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', instance.template, (0, None), (False, None)
		yield 'value', Array, (0, None, (instance.length,), name_type_map['Char']), (False, None)

	def __new__(self, context=None, arg=0, template=None, set_default=True):
		return ''

	@staticmethod
	def from_stream(stream, context=None, arg=0, template=None):
		length = template.from_stream(stream)
		chars = stream.read(length)
		return chars.decode(errors="surrogateescape")

	@staticmethod
	def to_stream(instance, stream, context, arg=0, template=None):
		encoded_instance = instance.encode(errors="surrogateescape")
		template.to_stream(len(encoded_instance), stream, context)
		stream.write(encoded_instance)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		string_len = len(instance.encode(errors="surrogateescape"))
		return template.get_size(string_len, context) + string_len

	get_field = None
	_get_filtered_attribute_list = None

	@staticmethod
	def fmt_member(instance, indent=0):
		return repr(instance)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert isinstance(instance, str)
		template.validate_instance(instance.encode(errors="surrogateescape"), context)

	@staticmethod
	def from_value(value):
		return str(value)

