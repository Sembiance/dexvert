from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiEmitterModifier(NiObject):

	__name__ = 'NiEmitterModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.next_modifier = name_type_map['Ref'](self.context, 0, name_type_map['NiEmitterModifier'])
		self.controller = name_type_map['Ptr'](self.context, 0, name_type_map['NiParticleSystemController'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'next_modifier', name_type_map['Ref'], (0, name_type_map['NiEmitterModifier']), (False, None), (None, None)
		yield 'controller', name_type_map['Ptr'], (0, name_type_map['NiParticleSystemController']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'next_modifier', name_type_map['Ref'], (0, name_type_map['NiEmitterModifier']), (False, None)
		yield 'controller', name_type_map['Ptr'], (0, name_type_map['NiParticleSystemController']), (False, None)
