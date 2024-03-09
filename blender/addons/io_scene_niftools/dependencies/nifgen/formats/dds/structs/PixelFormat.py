from nifgen.base_struct import BaseStruct
from nifgen.formats.dds.imports import name_type_map


class PixelFormat(BaseStruct):

	__name__ = 'PixelFormat'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Always 32.
		self.size = name_type_map['Uint'].from_value(32)

		# Non-zero for DX9, zero for DX10.
		self.flags = name_type_map['PixelFormatFlags'](self.context, 0, None)

		# Determines compression type. Zero means no compression.
		self.four_c_c = name_type_map['FourCC'](self.context, 0, None)

		# For non-compressed types, this is either 24 or 32 depending on whether there is an alpha channel. For compressed types, this describes the number of bits per block, which can be either 256 or 512.
		self.bit_count = name_type_map['Uint'](self.context, 0, None)

		# For non-compressed types, this determines the red mask. Usually 0x00FF0000. Is zero for compressed textures.
		self.r_mask = name_type_map['Uint'](self.context, 0, None)

		# For non-compressed types, this determines
		# the green mask. Usually 0x0000FF00. Is zero for compressed textures.
		self.g_mask = name_type_map['Uint'](self.context, 0, None)

		# For non-compressed types, this determines
		# the blue mask. Usually 0x00FF0000. Is zero for compressed textures.
		self.b_mask = name_type_map['Uint'](self.context, 0, None)

		# For non-compressed types, this determines
		# the alpha mask. Usually 0x00000000 if there is no alpha channel and 0xFF000000 if there is an alpha channel. Is zero for compressed textures.
		self.a_mask = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'size', name_type_map['Uint'], (0, None), (False, 32), (None, None)
		yield 'flags', name_type_map['PixelFormatFlags'], (0, None), (False, None), (None, None)
		yield 'four_c_c', name_type_map['FourCC'], (0, None), (False, None), (None, None)
		yield 'bit_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'r_mask', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'g_mask', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'b_mask', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'a_mask', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'size', name_type_map['Uint'], (0, None), (False, 32)
		yield 'flags', name_type_map['PixelFormatFlags'], (0, None), (False, None)
		yield 'four_c_c', name_type_map['FourCC'], (0, None), (False, None)
		yield 'bit_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'r_mask', name_type_map['Uint'], (0, None), (False, None)
		yield 'g_mask', name_type_map['Uint'], (0, None), (False, None)
		yield 'b_mask', name_type_map['Uint'], (0, None), (False, None)
		yield 'a_mask', name_type_map['Uint'], (0, None), (False, None)
