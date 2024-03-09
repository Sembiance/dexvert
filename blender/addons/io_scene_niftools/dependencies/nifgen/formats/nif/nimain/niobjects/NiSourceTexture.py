from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTexture import NiTexture


class NiSourceTexture(NiTexture):

	"""
	Describes texture source and properties.
	"""

	__name__ = 'NiSourceTexture'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Is the texture external?
		self.use_external = name_type_map['Byte'].from_value(1)
		self.use_internal = name_type_map['Byte'].from_value(1)

		# The external texture file name.

		# The original source filename of the image embedded by the referred NiPixelData object.
		self.file_name = name_type_map['FilePath'](self.context, 0, None)

		# NiPixelData or NiPersistentSrcTextureRendererData
		self.pixel_data = name_type_map['Ref'](self.context, 0, name_type_map['NiPixelFormat'])

		# A set of preferences for the texture format. They are a request only and the renderer may ignore them.
		self.format_prefs = name_type_map['FormatPrefs'](self.context, 0, None)

		# If set, then the application cannot assume that any dynamic changes to the pixel data will show in the rendered image.
		self.is_static = name_type_map['Byte'].from_value(1)

		# A hint to the renderer that the texture can be loaded directly from a texture file into a renderer-specific resource, bypassing the NiPixelData object.
		self.direct_render = name_type_map['Bool'].from_value(True)

		# Pixel Data is NiPersistentSrcTextureRendererData instead of NiPixelData.
		self.persist_render_data = name_type_map['Bool'].from_value(False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'use_external', name_type_map['Byte'], (0, None), (False, 1), (None, None)
		yield 'use_internal', name_type_map['Byte'], (0, None), (False, 1), (lambda context: context.version <= 167772419, True)
		yield 'file_name', name_type_map['FilePath'], (0, None), (False, None), (None, True)
		yield 'file_name', name_type_map['FilePath'], (0, None), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'pixel_data', name_type_map['Ref'], (0, name_type_map['NiPixelFormat']), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'pixel_data', name_type_map['Ref'], (0, name_type_map['NiPixelFormat']), (False, None), (lambda context: context.version <= 167772419, True)
		yield 'pixel_data', name_type_map['Ref'], (0, name_type_map['NiPixelFormat']), (False, None), (lambda context: context.version >= 167772420, True)
		yield 'format_prefs', name_type_map['FormatPrefs'], (0, None), (False, None), (None, None)
		yield 'is_static', name_type_map['Byte'], (0, None), (False, 1), (None, None)
		yield 'direct_render', name_type_map['Bool'], (0, None), (False, True), (lambda context: context.version >= 167837799, None)
		yield 'persist_render_data', name_type_map['Bool'], (0, None), (False, False), (lambda context: context.version >= 335675396, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'use_external', name_type_map['Byte'], (0, None), (False, 1)
		if instance.context.version <= 167772419 and instance.use_external == 0:
			yield 'use_internal', name_type_map['Byte'], (0, None), (False, 1)
		if instance.use_external == 1:
			yield 'file_name', name_type_map['FilePath'], (0, None), (False, None)
		if instance.context.version >= 167837696 and instance.use_external == 0:
			yield 'file_name', name_type_map['FilePath'], (0, None), (False, None)
		if instance.context.version >= 167837696 and instance.use_external == 1:
			yield 'pixel_data', name_type_map['Ref'], (0, name_type_map['NiPixelFormat']), (False, None)
		if instance.context.version <= 167772419 and instance.use_external == (0 and (instance.use_internal == 1)):
			yield 'pixel_data', name_type_map['Ref'], (0, name_type_map['NiPixelFormat']), (False, None)
		if instance.context.version >= 167772420 and instance.use_external == 0:
			yield 'pixel_data', name_type_map['Ref'], (0, name_type_map['NiPixelFormat']), (False, None)
		yield 'format_prefs', name_type_map['FormatPrefs'], (0, None), (False, None)
		yield 'is_static', name_type_map['Byte'], (0, None), (False, 1)
		if instance.context.version >= 167837799:
			yield 'direct_render', name_type_map['Bool'], (0, None), (False, True)
		if instance.context.version >= 335675396:
			yield 'persist_render_data', name_type_map['Bool'], (0, None), (False, False)
