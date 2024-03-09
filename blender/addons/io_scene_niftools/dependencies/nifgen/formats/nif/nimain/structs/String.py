from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class String(BaseStruct):

	"""
	A string type.
	"""

	__name__ = 'string'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The normal string.
		self.string = name_type_map['SizedString'](self.context, 0, None)

		# The string index.
		self.index = name_type_map['NiFixedString'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'string', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'index', name_type_map['NiFixedString'], (0, None), (False, None), (lambda context: context.version >= 335609859, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 335544325:
			yield 'string', name_type_map['SizedString'], (0, None), (False, None)
		if instance.context.version >= 335609859:
			yield 'index', name_type_map['NiFixedString'], (0, None), (False, None)

	def __new__(self, context, arg=0, template=None, set_default=True):
		return ''

	@staticmethod
	def from_stream(stream, context, arg=0, template=None):
		if context.version <= 335544325:
			return name_type_map["SizedString"].from_stream(stream, context, 0, None)
		if context.version >= 335609859:
			return name_type_map["NiFixedString"].from_stream(stream, context, 0, None)

	@staticmethod
	def to_stream(instance, stream, context, arg=0, template=None):
		if stream.context.version <= 335544325:
			name_type_map["SizedString"].to_stream(instance, stream, context)
		if stream.context.version >= 335609859:
			name_type_map["NiFixedString"].to_stream(instance, stream, context)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		if context.version <= 335544325:
			return name_type_map["SizedString"].get_size(instance, context)
		if context.version >= 335609859:
			return name_type_map["NiFixedString"].get_size(instance, context)

	get_field = None
	_get_filtered_attribute_list = None

	@staticmethod
	def fmt_member(instance, indent=0):
		return repr(instance)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		# either it contained a sizedstring or it referred to one in the header
		return name_type_map["SizedString"].validate_instance(instance, context, 0, None)

	@staticmethod
	def from_value(value):
		return str(value)

