from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class FormatPrefs(BaseStruct):

	"""
	NiTexture::FormatPrefs. These preferences are a request to the renderer to use a format the most closely matches the settings and may be ignored.
	"""

	__name__ = 'FormatPrefs'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Requests the way the image will be stored.
		self.pixel_layout = name_type_map['PixelLayout'](self.context, 0, None)

		# Requests if mipmaps are used or not.
		self.use_mipmaps = name_type_map['MipMapFormat'].MIP_FMT_DEFAULT

		# Requests no alpha, 1-bit alpha, or
		self.alpha_format = name_type_map['AlphaFormat'].ALPHA_DEFAULT
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pixel_layout', name_type_map['PixelLayout'], (0, None), (False, None), (None, None)
		yield 'use_mipmaps', name_type_map['MipMapFormat'], (0, None), (False, name_type_map['MipMapFormat'].MIP_FMT_DEFAULT), (None, None)
		yield 'alpha_format', name_type_map['AlphaFormat'], (0, None), (False, name_type_map['AlphaFormat'].ALPHA_DEFAULT), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pixel_layout', name_type_map['PixelLayout'], (0, None), (False, None)
		yield 'use_mipmaps', name_type_map['MipMapFormat'], (0, None), (False, name_type_map['MipMapFormat'].MIP_FMT_DEFAULT)
		yield 'alpha_format', name_type_map['AlphaFormat'], (0, None), (False, name_type_map['AlphaFormat'].ALPHA_DEFAULT)
