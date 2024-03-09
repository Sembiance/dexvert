from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiPixelFormat import NiPixelFormat


class NiPersistentSrcTextureRendererData(NiPixelFormat):

	__name__ = 'NiPersistentSrcTextureRendererData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.palette = name_type_map['Ref'](self.context, 0, name_type_map['NiPalette'])
		self.num_mipmaps = name_type_map['Uint'](self.context, 0, None)
		self.bytes_per_pixel = name_type_map['Uint'](self.context, 0, None)
		self.mipmaps = Array(self.context, 0, None, (0,), name_type_map['MipMap'])
		self.num_pixels = name_type_map['Uint'](self.context, 0, None)
		self.pad_num_pixels = name_type_map['Uint'](self.context, 0, None)
		self.num_faces = name_type_map['Uint'](self.context, 0, None)
		self.platform = name_type_map['PlatformID'](self.context, 0, None)
		self.renderer = name_type_map['RendererID'](self.context, 0, None)
		self.pixel_data = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'palette', name_type_map['Ref'], (0, name_type_map['NiPalette']), (False, None), (None, None)
		yield 'num_mipmaps', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bytes_per_pixel', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'mipmaps', Array, (0, None, (None,), name_type_map['MipMap']), (False, None), (None, None)
		yield 'num_pixels', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'pad_num_pixels', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335675398, None)
		yield 'num_faces', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'platform', name_type_map['PlatformID'], (0, None), (False, None), (lambda context: context.version <= 503382016, None)
		yield 'renderer', name_type_map['RendererID'], (0, None), (False, None), (lambda context: context.version >= 503382017, None)
		yield 'pixel_data', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'palette', name_type_map['Ref'], (0, name_type_map['NiPalette']), (False, None)
		yield 'num_mipmaps', name_type_map['Uint'], (0, None), (False, None)
		yield 'bytes_per_pixel', name_type_map['Uint'], (0, None), (False, None)
		yield 'mipmaps', Array, (0, None, (instance.num_mipmaps,), name_type_map['MipMap']), (False, None)
		yield 'num_pixels', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335675398:
			yield 'pad_num_pixels', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_faces', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 503382016:
			yield 'platform', name_type_map['PlatformID'], (0, None), (False, None)
		if instance.context.version >= 503382017:
			yield 'renderer', name_type_map['RendererID'], (0, None), (False, None)
		yield 'pixel_data', Array, (0, None, (instance.num_pixels * instance.num_faces,), name_type_map['Byte']), (False, None)
