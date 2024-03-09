from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSPSysRecycleBoundModifier(NiPSysModifier):

	__name__ = 'BSPSysRecycleBoundModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bound_offset = name_type_map['Vector3'](self.context, 0, None)
		self.bound_extent = name_type_map['Vector3'](self.context, 0, None)
		self.bound_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bound_offset', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'bound_extent', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'bound_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bound_offset', name_type_map['Vector3'], (0, None), (False, None)
		yield 'bound_extent', name_type_map['Vector3'], (0, None), (False, None)
		yield 'bound_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
