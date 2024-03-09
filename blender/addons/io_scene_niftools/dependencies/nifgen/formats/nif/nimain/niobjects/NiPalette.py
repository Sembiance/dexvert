from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPalette(NiObject):

	"""
	NiPalette objects represent mappings from 8-bit indices to 24-bit RGB or 32-bit RGBA colors.
	"""

	__name__ = 'NiPalette'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Not boolean but used as one, always 8-bit.
		self.has_alpha = name_type_map['Byte'](self.context, 0, None)

		# The number of palette entries. Always 256 but can also be 16.
		self.num_entries = name_type_map['Uint'].from_value(256)

		# The color palette.
		self.palette = Array(self.context, 0, None, (0,), name_type_map['ByteColor4'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_alpha', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'num_entries', name_type_map['Uint'], (0, None), (False, 256), (None, None)
		yield 'palette', Array, (0, None, (16,), name_type_map['ByteColor4']), (False, None), (None, True)
		yield 'palette', Array, (0, None, (256,), name_type_map['ByteColor4']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_alpha', name_type_map['Byte'], (0, None), (False, None)
		yield 'num_entries', name_type_map['Uint'], (0, None), (False, 256)
		if instance.num_entries == 16:
			yield 'palette', Array, (0, None, (16,), name_type_map['ByteColor4']), (False, None)
		if instance.num_entries != 16:
			yield 'palette', Array, (0, None, (256,), name_type_map['ByteColor4']), (False, None)
