from nifgen.formats.voxelskirt.compounds.Material import Material
from nifgen.formats.voxelskirt.imports import name_type_map


class EntityGroup(Material):

	"""
	32 bytes
	describes a list of instances of one entity
	"""

	__name__ = 'EntityGroup'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# -1
		self.ff = name_type_map['Int'](self.context, 0, None)

		# -1, 0 for PC
		self.ff_or_zero = name_type_map['Int'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ff', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'ff_or_zero', name_type_map['Int'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ff', name_type_map['Int'], (0, None), (False, None)
		yield 'ff_or_zero', name_type_map['Int'], (0, None), (False, None)
