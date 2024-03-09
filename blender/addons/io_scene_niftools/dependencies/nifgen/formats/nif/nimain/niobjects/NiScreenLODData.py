from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiLODData import NiLODData


class NiScreenLODData(NiLODData):

	"""
	NiScreenLODData controls switching LOD levels based on proportion of the screen that a bound would include.
	"""

	__name__ = 'NiScreenLODData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)
		self.world_bounding_sphere = name_type_map['NiBound'](self.context, 0, None)
		self.num_proportions = name_type_map['Uint'](self.context, 0, None)
		self.proportion_levels = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, None)
		yield 'world_bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, None)
		yield 'num_proportions', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'proportion_levels', Array, (0, None, (None,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		yield 'world_bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		yield 'num_proportions', name_type_map['Uint'], (0, None), (False, None)
		yield 'proportion_levels', Array, (0, None, (instance.num_proportions,), name_type_map['Float']), (False, None)
