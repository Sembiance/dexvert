from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiRawImageData(NiObject):

	"""
	LEGACY (pre-10.1)
	Raw image data.
	"""

	__name__ = 'NiRawImageData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Image width
		self.width = name_type_map['Uint'](self.context, 0, None)

		# Image height
		self.height = name_type_map['Uint'](self.context, 0, None)

		# The format of the raw image data.
		self.image_type = name_type_map['ImageType'](self.context, 0, None)

		# Image pixel data.
		self.rgb_image_data = Array(self.context, 0, None, (0,), name_type_map['ByteColor3'])

		# Image pixel data.
		self.rgba_image_data = Array(self.context, 0, None, (0,), name_type_map['ByteColor4'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'width', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'height', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'image_type', name_type_map['ImageType'], (0, None), (False, None), (None, None)
		yield 'rgb_image_data', Array, (0, None, (None, None,), name_type_map['ByteColor3']), (False, None), (None, True)
		yield 'rgba_image_data', Array, (0, None, (None, None,), name_type_map['ByteColor4']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'width', name_type_map['Uint'], (0, None), (False, None)
		yield 'height', name_type_map['Uint'], (0, None), (False, None)
		yield 'image_type', name_type_map['ImageType'], (0, None), (False, None)
		if instance.image_type == 1:
			yield 'rgb_image_data', Array, (0, None, (instance.width, instance.height,), name_type_map['ByteColor3']), (False, None)
		if instance.image_type == 2:
			yield 'rgba_image_data', Array, (0, None, (instance.width, instance.height,), name_type_map['ByteColor4']), (False, None)
