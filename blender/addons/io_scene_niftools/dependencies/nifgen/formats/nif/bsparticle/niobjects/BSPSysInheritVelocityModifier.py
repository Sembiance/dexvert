from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSPSysInheritVelocityModifier(NiPSysModifier):

	__name__ = 'BSPSysInheritVelocityModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.inherit_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		self.chance_to_inherit = name_type_map['Float'].from_value(100.0)
		self.velocity_multiplier = name_type_map['Float'].from_value(0.5)
		self.velocity_variation = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'inherit_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'chance_to_inherit', name_type_map['Float'], (0, None), (False, 100.0), (None, None)
		yield 'velocity_multiplier', name_type_map['Float'], (0, None), (False, 0.5), (None, None)
		yield 'velocity_variation', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'inherit_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'chance_to_inherit', name_type_map['Float'], (0, None), (False, 100.0)
		yield 'velocity_multiplier', name_type_map['Float'], (0, None), (False, 0.5)
		yield 'velocity_variation', name_type_map['Float'], (0, None), (False, None)
