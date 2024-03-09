import nifgen.formats.nif as NifFormat
from nifgen.formats.dds import DdsFile
from nifgen.formats.dds.enums.FourCC import FourCC
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPixelFormat(NiObject):

	"""
	NiPixelFormat is not the parent to NiPixelData/NiPersistentSrcTextureRendererData,
	but actually a member class loaded at the top of each. The two classes are not related.
	However, faking this inheritance is useful for several things.
	"""

	__name__ = 'NiPixelFormat'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The format of the pixels in this internally stored image.
		self.pixel_format = name_type_map['PixelFormat'](self.context, 0, None)

		# 0x000000ff (for 24bpp and 32bpp) or 0x00000000 (for 8bpp)
		self.red_mask = name_type_map['Uint'](self.context, 0, None)

		# 0x0000ff00 (for 24bpp and 32bpp) or 0x00000000 (for 8bpp)
		self.green_mask = name_type_map['Uint'](self.context, 0, None)

		# 0x00ff0000 (for 24bpp and 32bpp) or 0x00000000 (for 8bpp)
		self.blue_mask = name_type_map['Uint'](self.context, 0, None)

		# 0xff000000 (for 32bpp) or 0x00000000 (for 24bpp and 8bpp)
		self.alpha_mask = name_type_map['Uint'](self.context, 0, None)

		# Bits per pixel, 0 (Compressed), 8, 24 or 32.
		self.bits_per_pixel = name_type_map['Uint'](self.context, 0, None)

		# [96,8,130,0,0,65,0,0] if 24 bits per pixel
		# [129,8,130,32,0,65,12,0] if 32 bits per pixel
		# [34,0,0,0,0,0,0,0] if 8 bits per pixel
		# [X,0,0,0,0,0,0,0] if 0 (Compressed) bits per pixel where X = PixelFormat
		self.old_fast_compare = Array(self.context, 0, None, (0,), name_type_map['Byte'])

		# Seems to always be zero.
		self.tiling = name_type_map['PixelTiling'](self.context, 0, None)

		# Bits per pixel, 0 (Compressed), 8, 24 or 32.
		self.bits_per_pixel = name_type_map['Byte'](self.context, 0, None)
		self.renderer_hint = name_type_map['Uint'](self.context, 0, None)
		self.extra_data = name_type_map['Uint'](self.context, 0, None)
		self.flags = name_type_map['Byte'](self.context, 0, None)
		self.tiling = name_type_map['PixelTiling'](self.context, 0, None)
		self.s_r_g_b_space = name_type_map['Bool'](self.context, 0, None)

		# Channel Data
		self.channels = Array(self.context, 0, None, (0,), name_type_map['PixelFormatComponent'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pixel_format', name_type_map['PixelFormat'], (0, None), (False, None), (None, None)
		yield 'red_mask', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'green_mask', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'blue_mask', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'alpha_mask', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'bits_per_pixel', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'old_fast_compare', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'tiling', name_type_map['PixelTiling'], (0, None), (False, None), (lambda context: 167837696 <= context.version <= 168034305, None)
		yield 'bits_per_pixel', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 168034306, None)
		yield 'renderer_hint', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 168034306, None)
		yield 'extra_data', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 168034306, None)
		yield 'flags', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 168034306, None)
		yield 'tiling', name_type_map['PixelTiling'], (0, None), (False, None), (lambda context: context.version >= 168034306, None)
		yield 's_r_g_b_space', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335740932, None)
		yield 'channels', Array, (0, None, (4,), name_type_map['PixelFormatComponent']), (False, None), (lambda context: context.version >= 168034306, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pixel_format', name_type_map['PixelFormat'], (0, None), (False, None)
		if instance.context.version <= 168034305:
			yield 'red_mask', name_type_map['Uint'], (0, None), (False, None)
			yield 'green_mask', name_type_map['Uint'], (0, None), (False, None)
			yield 'blue_mask', name_type_map['Uint'], (0, None), (False, None)
			yield 'alpha_mask', name_type_map['Uint'], (0, None), (False, None)
			yield 'bits_per_pixel', name_type_map['Uint'], (0, None), (False, None)
			yield 'old_fast_compare', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		if 167837696 <= instance.context.version <= 168034305:
			yield 'tiling', name_type_map['PixelTiling'], (0, None), (False, None)
		if instance.context.version >= 168034306:
			yield 'bits_per_pixel', name_type_map['Byte'], (0, None), (False, None)
			yield 'renderer_hint', name_type_map['Uint'], (0, None), (False, None)
			yield 'extra_data', name_type_map['Uint'], (0, None), (False, None)
			yield 'flags', name_type_map['Byte'], (0, None), (False, None)
			yield 'tiling', name_type_map['PixelTiling'], (0, None), (False, None)
		if instance.context.version >= 335740932:
			yield 's_r_g_b_space', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 168034306:
			yield 'channels', Array, (0, None, (4,), name_type_map['PixelFormatComponent']), (False, None)

	def _get_pixeldata_stream(self):
		return bytes(self.pixel_data)

	def save_as_dds(self, stream):
		"""Save image as DDS file."""
		# set up header and pixel data
		file = DdsFile()

		# create header, depending on the format
		if self.pixel_format in (NifFormat.classes.PixelFormat.FMT_RGB,
								 NifFormat.classes.PixelFormat.FMT_RGBA):
			# uncompressed RGB(A)
			file.flags.caps = 1
			file.flags.height = 1
			file.flags.width = 1
			file.flags.pixel_format = 1
			file.flags.mipmap_count = 1
			file.flags.linear_size = 1
			file.height = self.mipmaps[0].height
			file.width = self.mipmaps[0].width
			file.linear_size = len(self.pixel_data) // self.num_pixels # we want it to be 1 for version <= 10.2.0.0?
			file.mipmap_count = len(self.mipmaps)
			file.pixel_format.flags.four_c_c = 0
			file.pixel_format.flags.rgb = 1
			file.pixel_format.four_c_c = FourCC.LINEAR
			file.pixel_format.bit_count = self.bits_per_pixel
			if not self.channels:
				file.pixel_format.r_mask = self.red_mask
				file.pixel_format.g_mask = self.green_mask
				file.pixel_format.b_mask = self.blue_mask
				file.pixel_format.a_mask = self.alpha_mask
			else:
				bit_pos = 0
				for i, channel in enumerate(self.channels):
					mask = (2 ** channel.bits_per_channel - 1) << bit_pos
					if channel.type == NifFormat.classes.PixelComponent.COMP_RED:
						file.pixel_format.r_mask = mask
					elif channel.type == NifFormat.classes.PixelComponent.COMP_GREEN:
						file.pixel_format.g_mask = mask
					elif channel.type == NifFormat.classes.PixelComponent.COMP_BLUE:
						file.pixel_format.b_mask = mask
					elif channel.type == NifFormat.classes.PixelComponent.COMP_ALPHA:
						file.pixel_format.a_mask = mask
					bit_pos += channel.bits_per_channel
			file.caps_1.complex = 1
			file.caps_1.texture = 1
			file.caps_1.mipmap = 1
			file.buffer = self._get_pixeldata_stream()
		elif self.pixel_format == NifFormat.classes.PixelFormat.FMT_DXT1:
			# format used in Megami Tensei: Imagine and Bully SE
			file.flags.caps = 1
			file.flags.height = 1
			file.flags.width = 1
			file.flags.pixel_format = 1
			file.flags.mipmap_count = 1
			file.flags.linear_size = 0
			file.height = self.mipmaps[0].height
			file.width = self.mipmaps[0].width
			file.linear_size = 0
			file.mipmap_count = len(self.mipmaps)
			file.pixel_format.flags.four_c_c = 1
			file.pixel_format.four_c_c = FourCC.DXT1
			file.pixel_format.bit_count = 0
			file.pixel_format.r_mask = 0
			file.pixel_format.g_mask = 0
			file.pixel_format.b_mask = 0
			file.pixel_format.a_mask = 0
			file.caps_1.complex = 1
			file.caps_1.texture = 1
			file.caps_1.mipmap = 1
			file.buffer = self._get_pixeldata_stream()
		elif self.pixel_format in (NifFormat.classes.PixelFormat.FMT_DXT3,
								   NifFormat.classes.PixelFormat.FMT_DXT5):
			# format used in Megami Tensei: Imagine
			file.flags.caps = 1
			file.flags.height = 1
			file.flags.width = 1
			file.flags.pixel_format = 1
			file.flags.mipmap_count = 1
			file.flags.linear_size = 0
			file.height = self.mipmaps[0].height
			file.width = self.mipmaps[0].width
			file.linear_size = 0
			file.mipmap_count = len(self.mipmaps)
			file.pixel_format.flags.four_c_c = 1
			file.pixel_format.four_c_c = FourCC.DXT5
			file.pixel_format.bit_count = 0
			file.pixel_format.r_mask = 0
			file.pixel_format.g_mask = 0
			file.pixel_format.b_mask = 0
			file.pixel_format.a_mask = 0
			file.caps_1.complex = 1
			file.caps_1.texture = 1
			file.caps_1.mipmap = 1
			file.buffer = self._get_pixeldata_stream()
		else:
			raise ValueError(
				"cannot save pixel format %i as DDS" % self.pixel_format)

		file.write(stream)

