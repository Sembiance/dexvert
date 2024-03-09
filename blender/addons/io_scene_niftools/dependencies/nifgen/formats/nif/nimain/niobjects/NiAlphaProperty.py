from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiAlphaProperty(NiProperty):

	"""
	Transparency. Flags 0x00ED.
	"""

	__name__ = 'NiAlphaProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['AlphaFlags'].from_value(4844)

		# Threshold for alpha testing
		self.threshold = name_type_map['Byte'].from_value(128)

		# Unknown
		self.unknown_short_1 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_int_2 = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['AlphaFlags'], (0, None), (False, 4844), (None, None)
		yield 'threshold', name_type_map['Byte'], (0, None), (False, 128), (None, None)
		yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 33751040, None)
		yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None), (lambda context: 335741185 <= context.version <= 335741186, None)
		yield 'unknown_int_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 33751040, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['AlphaFlags'], (0, None), (False, 4844)
		yield 'threshold', name_type_map['Byte'], (0, None), (False, 128)
		if instance.context.version <= 33751040:
			yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None)
		if 335741185 <= instance.context.version <= 335741186:
			yield 'unknown_short_1', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 33751040:
			yield 'unknown_int_2', name_type_map['Uint'], (0, None), (False, None)
