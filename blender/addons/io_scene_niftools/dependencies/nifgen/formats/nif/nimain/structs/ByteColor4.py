from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class ByteColor4(BaseStruct):

	"""
	A color with alpha (red, green, blue, alpha).
	"""

	__name__ = 'ByteColor4'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Red color component.
		self.r = name_type_map['Byte'](self.context, 0, None)

		# Green color component.
		self.g = name_type_map['Byte'](self.context, 0, None)

		# Blue color component.
		self.b = name_type_map['Byte'](self.context, 0, None)

		# Alpha color component.
		self.a = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'r', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'g', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'a', name_type_map['Byte'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'r', name_type_map['Byte'], (0, None), (False, None)
		yield 'g', name_type_map['Byte'], (0, None), (False, None)
		yield 'b', name_type_map['Byte'], (0, None), (False, None)
		yield 'a', name_type_map['Byte'], (0, None), (False, None)
