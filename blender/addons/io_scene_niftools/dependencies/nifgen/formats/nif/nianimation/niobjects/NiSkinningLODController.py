from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiSkinningLODController(NiTimeController):

	"""
	Defines the levels of detail for a given character and dictates the character's current LOD.
	"""

	__name__ = 'NiSkinningLODController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.current_lod = name_type_map['Uint'](self.context, 0, None)
		self.num_bones = name_type_map['Uint'](self.context, 0, None)
		self.bones = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ref'])
		self.num_skins = name_type_map['Uint'](self.context, 0, None)
		self.skins = Array(self.context, 0, name_type_map['NiMesh'], (0,), name_type_map['Ref'])
		self.num_lod_levels = name_type_map['Uint'](self.context, 0, None)
		self.l_o_ds = Array(self.context, 0, None, (0,), name_type_map['LODInfo'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'current_lod', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_skins', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'skins', Array, (0, name_type_map['NiMesh'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_lod_levels', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'l_o_ds', Array, (0, None, (None,), name_type_map['LODInfo']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'current_lod', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (instance.num_bones,), name_type_map['Ref']), (False, None)
		yield 'num_skins', name_type_map['Uint'], (0, None), (False, None)
		yield 'skins', Array, (0, name_type_map['NiMesh'], (instance.num_skins,), name_type_map['Ref']), (False, None)
		yield 'num_lod_levels', name_type_map['Uint'], (0, None), (False, None)
		yield 'l_o_ds', Array, (0, None, (instance.num_lod_levels,), name_type_map['LODInfo']), (False, None)
