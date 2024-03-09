from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiImage(NiObject):

	"""
	LEGACY (pre-10.1)
	"""

	__name__ = 'NiImage'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 0 if the texture is internal to the NIF file.
		self.use_external = name_type_map['Byte'](self.context, 0, None)

		# The filepath to the texture.
		self.file_name = name_type_map['FilePath'](self.context, 0, None)

		# Link to the internally stored image data.
		self.image_data = name_type_map['Ref'](self.context, 0, name_type_map['NiRawImageData'])
		self.unknown_int = name_type_map['Uint'].from_value(7)
		self.unknown_float = name_type_map['Float'].from_value(128.5)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'use_external', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'file_name', name_type_map['FilePath'], (0, None), (False, None), (None, True)
		yield 'image_data', name_type_map['Ref'], (0, name_type_map['NiRawImageData']), (False, None), (None, True)
		yield 'unknown_int', name_type_map['Uint'], (0, None), (False, 7), (None, None)
		yield 'unknown_float', name_type_map['Float'], (0, None), (False, 128.5), (lambda context: context.version >= 50397184, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'use_external', name_type_map['Byte'], (0, None), (False, None)
		if instance.use_external != 0:
			yield 'file_name', name_type_map['FilePath'], (0, None), (False, None)
		if instance.use_external == 0:
			yield 'image_data', name_type_map['Ref'], (0, name_type_map['NiRawImageData']), (False, None)
		yield 'unknown_int', name_type_map['Uint'], (0, None), (False, 7)
		if instance.context.version >= 50397184:
			yield 'unknown_float', name_type_map['Float'], (0, None), (False, 128.5)
