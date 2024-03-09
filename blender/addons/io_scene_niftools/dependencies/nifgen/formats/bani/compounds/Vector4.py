from nifgen.base_struct import BaseStruct
from nifgen.formats.bani.imports import name_type_map


class Vector4(BaseStruct):

	"""
	A vector in 3D space (x,y,z).
	"""

	__name__ = 'Vector4'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# zeroth coordinate.
		self.w = name_type_map['Float'](self.context, 0, None)

		# First coordinate.
		self.x = name_type_map['Float'](self.context, 0, None)

		# Second coordinate.
		self.y = name_type_map['Float'](self.context, 0, None)

		# Third coordinate.
		self.z = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'w', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'x', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'w', name_type_map['Float'], (0, None), (False, None)
		yield 'x', name_type_map['Float'], (0, None), (False, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None)
