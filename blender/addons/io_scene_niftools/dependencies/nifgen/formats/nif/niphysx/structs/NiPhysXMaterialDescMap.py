from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiPhysXMaterialDescMap(BaseStruct):

	__name__ = 'NiPhysXMaterialDescMap'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.key = name_type_map['Ushort'](self.context, 0, None)
		self.material = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXMaterialDesc'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'key', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'material', name_type_map['Ref'], (0, name_type_map['NiPhysXMaterialDesc']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'key', name_type_map['Ushort'], (0, None), (False, None)
		yield 'material', name_type_map['Ref'], (0, name_type_map['NiPhysXMaterialDesc']), (False, None)
