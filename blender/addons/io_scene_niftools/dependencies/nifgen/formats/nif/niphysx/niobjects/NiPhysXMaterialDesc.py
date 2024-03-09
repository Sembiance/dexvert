from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXMaterialDesc(NiObject):

	"""
	For serializing NxMaterialDesc objects.
	"""

	__name__ = 'NiPhysXMaterialDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.index = name_type_map['Ushort'](self.context, 0, None)
		self.num_states = name_type_map['Uint'](self.context, 0, None)
		self.material_descs = Array(self.context, 0, None, (0,), name_type_map['NxMaterialDesc'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_states', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'material_descs', Array, (0, None, (None,), name_type_map['NxMaterialDesc']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_states', name_type_map['Uint'], (0, None), (False, None)
		yield 'material_descs', Array, (0, None, (instance.num_states,), name_type_map['NxMaterialDesc']), (False, None)
