from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiLODData import NiLODData


class NiRangeLODData(NiLODData):

	"""
	NiRangeLODData controls switching LOD levels based on Z depth from the camera to the NiLODNode.
	"""

	__name__ = 'NiRangeLODData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.lod_center = name_type_map['Vector3'](self.context, 0, None)
		self.num_lod_levels = name_type_map['Uint'](self.context, 0, None)
		self.lod_levels = Array(self.context, 0, None, (0,), name_type_map['LODRange'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lod_center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'num_lod_levels', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'lod_levels', Array, (0, None, (None,), name_type_map['LODRange']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lod_center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'num_lod_levels', name_type_map['Uint'], (0, None), (False, None)
		yield 'lod_levels', Array, (0, None, (instance.num_lod_levels,), name_type_map['LODRange']), (False, None)
