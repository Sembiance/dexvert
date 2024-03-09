from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysMeshUpdateModifier import NiPSysMeshUpdateModifier


class BSPSysHavokUpdateModifier(NiPSysMeshUpdateModifier):

	__name__ = 'BSPSysHavokUpdateModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.modifier = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysModifier'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'modifier', name_type_map['Ref'], (0, name_type_map['NiPSysModifier']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'modifier', name_type_map['Ref'], (0, name_type_map['NiPSysModifier']), (False, None)
