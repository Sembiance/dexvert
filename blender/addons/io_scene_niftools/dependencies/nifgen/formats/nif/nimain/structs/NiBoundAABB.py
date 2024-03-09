from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiBoundAABB(BaseStruct):

	"""
	Divinity 2 specific NiBound extension.
	"""

	__name__ = 'NiBoundAABB'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_corners = name_type_map['Ushort'].from_value(2)

		# Corners are only non-zero if Num Corners is 2. Hardcoded to 2.
		self.corners = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_corners', name_type_map['Ushort'], (0, None), (False, 2), (None, None)
		yield 'corners', Array, (0, None, (2,), name_type_map['Vector3']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_corners', name_type_map['Ushort'], (0, None), (False, 2)
		yield 'corners', Array, (0, None, (2,), name_type_map['Vector3']), (False, None)
