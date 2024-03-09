from nifgen.formats.nif.bsmain.niobjects.BSMultiBoundData import BSMultiBoundData
from nifgen.formats.nif.imports import name_type_map


class BSMultiBoundAABB(BSMultiBoundData):

	"""
	Bethesda-specific object.
	"""

	__name__ = 'BSMultiBoundAABB'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Position of the AABB's center
		self.position = name_type_map['Vector3'](self.context, 0, None)

		# Extent of the AABB in all directions
		self.extent = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'position', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'extent', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None)
		yield 'extent', name_type_map['Vector3'], (0, None), (False, None)
