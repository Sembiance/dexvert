from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiSwitchNode import NiSwitchNode


class NiLODNode(NiSwitchNode):

	"""
	Level of detail selector. Links to different levels of detail of the same model, used to switch a geometry at a specified distance.
	"""

	__name__ = 'NiLODNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.lod_center = name_type_map['Vector3'](self.context, 0, None)
		self.num_lod_levels = name_type_map['Uint'](self.context, 0, None)
		self.lod_levels = Array(self.context, 0, None, (0,), name_type_map['LODRange'])
		self.lod_level_data = name_type_map['Ref'](self.context, 0, name_type_map['NiLODData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lod_center', name_type_map['Vector3'], (0, None), (False, None), (lambda context: 67108866 <= context.version <= 167772416, None)
		yield 'num_lod_levels', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 167772416, None)
		yield 'lod_levels', Array, (0, None, (None,), name_type_map['LODRange']), (False, None), (lambda context: context.version <= 167772416, None)
		yield 'lod_level_data', name_type_map['Ref'], (0, name_type_map['NiLODData']), (False, None), (lambda context: context.version >= 167837696, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 67108866 <= instance.context.version <= 167772416:
			yield 'lod_center', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version <= 167772416:
			yield 'num_lod_levels', name_type_map['Uint'], (0, None), (False, None)
			yield 'lod_levels', Array, (0, None, (instance.num_lod_levels,), name_type_map['LODRange']), (False, None)
		if instance.context.version >= 167837696:
			yield 'lod_level_data', name_type_map['Ref'], (0, name_type_map['NiLODData']), (False, None)
