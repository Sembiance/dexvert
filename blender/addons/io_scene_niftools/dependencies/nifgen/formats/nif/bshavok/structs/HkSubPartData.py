from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HkSubPartData(BaseStruct):

	"""
	Bethesda Havok. Havok Information for packed TriStrip shapes.
	"""

	__name__ = 'hkSubPartData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.havok_filter = name_type_map['HavokFilter'](self.context, 0, None)

		# The number of vertices that form this sub shape.
		self.num_vertices = name_type_map['Uint'](self.context, 0, None)

		# The material of the subshape.
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'havok_filter', name_type_map['HavokFilter'], (0, None), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'havok_filter', name_type_map['HavokFilter'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
