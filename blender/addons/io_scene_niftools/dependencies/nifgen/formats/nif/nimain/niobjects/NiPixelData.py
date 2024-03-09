from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiPixelFormat import NiPixelFormat


class NiPixelData(NiPixelFormat):

	"""
	A texture.
	"""

	__name__ = 'NiPixelData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.palette = name_type_map['Ref'](self.context, 0, name_type_map['NiPalette'])
		self.num_mipmaps = name_type_map['Uint'](self.context, 0, None)
		self.bytes_per_pixel = name_type_map['Uint'](self.context, 0, None)
		self.mipmaps = Array(self.context, 0, None, (0,), name_type_map['MipMap'])
		self.num_pixels = name_type_map['Uint'](self.context, 0, None)
		self.num_faces = name_type_map['Uint'].from_value(1)
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
		yield 'num_faces', name_type_map['Uint'], (0, None), (False, 1), (lambda context: context.version >= 168034306, None)
		yield 'pixel_data', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'pixel_data', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (lambda context: context.version >= 168034306, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'palette', name_type_map['Ref'], (0, name_type_map['NiPalette']), (False, None)
		yield 'num_mipmaps', name_type_map['Uint'], (0, None), (False, None)
		yield 'bytes_per_pixel', name_type_map['Uint'], (0, None), (False, None)
		yield 'mipmaps', Array, (0, None, (instance.num_mipmaps,), name_type_map['MipMap']), (False, None)
		yield 'num_pixels', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 168034306:
			yield 'num_faces', name_type_map['Uint'], (0, None), (False, 1)
		if instance.context.version <= 168034305:
			yield 'pixel_data', Array, (0, None, (instance.num_pixels,), name_type_map['Byte']), (False, None)
		if instance.context.version >= 168034306:
			yield 'pixel_data', Array, (0, None, (instance.num_pixels * instance.num_faces,), name_type_map['Byte']), (False, None)
