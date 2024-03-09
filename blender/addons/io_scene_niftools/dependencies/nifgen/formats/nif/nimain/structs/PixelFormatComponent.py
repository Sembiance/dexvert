from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class PixelFormatComponent(BaseStruct):

	__name__ = 'PixelFormatComponent'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Component Type
		self.type = name_type_map['PixelComponent'](self.context, 0, None)

		# Data Storage Convention
		self.convention = name_type_map['PixelRepresentation'](self.context, 0, None)

		# Bits per component
		self.bits_per_channel = name_type_map['Byte'](self.context, 0, None)
		self.is_signed = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'type', name_type_map['PixelComponent'], (0, None), (False, None), (None, None)
		yield 'convention', name_type_map['PixelRepresentation'], (0, None), (False, None), (None, None)
		yield 'bits_per_channel', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'is_signed', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'type', name_type_map['PixelComponent'], (0, None), (False, None)
		yield 'convention', name_type_map['PixelRepresentation'], (0, None), (False, None)
		yield 'bits_per_channel', name_type_map['Byte'], (0, None), (False, None)
		yield 'is_signed', name_type_map['Bool'], (0, None), (False, None)
