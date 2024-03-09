from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.dds.imports import name_type_map


class Header(BaseStruct):

	__name__ = 'Header'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# DDS
		self.header_string = name_type_map['FixedString'](self.context, 4, None)

		# Always 124 + 4 bytes for headerstring, header ends at 128.
		self.size = name_type_map['Uint'].from_value(124)
		self.flags = name_type_map['HeaderFlags'](self.context, 0, None)

		# The texture height.
		self.height = name_type_map['Uint'](self.context, 0, None)

		# The texture width.
		self.width = name_type_map['Uint'](self.context, 0, None)
		self.linear_size = name_type_map['Uint'](self.context, 0, None)
		self.depth = name_type_map['Uint'].from_value(1)
		self.mipmap_count = name_type_map['Uint'](self.context, 0, None)
		self.reserved_1 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.pixel_format = name_type_map['PixelFormat'](self.context, 0, None)
		self.caps_1 = name_type_map['Caps1'](self.context, 0, None)
		self.caps_2 = name_type_map['Caps2'](self.context, 0, None)
		self.caps_3 = name_type_map['Uint'](self.context, 0, None)
		self.caps_4 = name_type_map['Uint'](self.context, 0, None)
		self.unused = name_type_map['Uint'](self.context, 0, None)
		self.dx_10 = name_type_map['Dxt10Header'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'header_string', name_type_map['FixedString'], (4, None), (False, None), (None, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, 124), (None, None)
		yield 'flags', name_type_map['HeaderFlags'], (0, None), (False, None), (None, None)
		yield 'height', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'width', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'linear_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'depth', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'mipmap_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'reserved_1', Array, (0, None, (11,), name_type_map['Uint']), (False, None), (None, None)
		yield 'pixel_format', name_type_map['PixelFormat'], (0, None), (False, None), (None, None)
		yield 'caps_1', name_type_map['Caps1'], (0, None), (False, None), (None, None)
		yield 'caps_2', name_type_map['Caps2'], (0, None), (False, None), (None, None)
		yield 'caps_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'caps_4', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unused', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'dx_10', name_type_map['Dxt10Header'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'header_string', name_type_map['FixedString'], (4, None), (False, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, 124)
		yield 'flags', name_type_map['HeaderFlags'], (0, None), (False, None)
		yield 'height', name_type_map['Uint'], (0, None), (False, None)
		yield 'width', name_type_map['Uint'], (0, None), (False, None)
		yield 'linear_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'depth', name_type_map['Uint'], (0, None), (False, 1)
		yield 'mipmap_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'reserved_1', Array, (0, None, (11,), name_type_map['Uint']), (False, None)
		yield 'pixel_format', name_type_map['PixelFormat'], (0, None), (False, None)
		yield 'caps_1', name_type_map['Caps1'], (0, None), (False, None)
		yield 'caps_2', name_type_map['Caps2'], (0, None), (False, None)
		yield 'caps_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'caps_4', name_type_map['Uint'], (0, None), (False, None)
		yield 'unused', name_type_map['Uint'], (0, None), (False, None)
		if instance.pixel_format.four_c_c == 808540228:
			yield 'dx_10', name_type_map['Dxt10Header'], (0, None), (False, None)
