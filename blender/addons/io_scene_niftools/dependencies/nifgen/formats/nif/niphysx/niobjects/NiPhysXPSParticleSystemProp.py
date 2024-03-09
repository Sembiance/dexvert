from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niphysx.niobjects.NiPhysXProp import NiPhysXProp


class NiPhysXPSParticleSystemProp(NiPhysXProp):

	"""
	A PhysX prop which holds information about a PhysX particle system prop.
	"""

	__name__ = 'NiPhysXPSParticleSystemProp'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_systems = name_type_map['Uint'](self.context, 0, None)
		self.systems = Array(self.context, 0, name_type_map['NiPhysXPSParticleSystem'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_systems', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'systems', Array, (0, name_type_map['NiPhysXPSParticleSystem'], (None,), name_type_map['Ptr']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_systems', name_type_map['Uint'], (0, None), (False, None)
		yield 'systems', Array, (0, name_type_map['NiPhysXPSParticleSystem'], (instance.num_systems,), name_type_map['Ptr']), (False, None)
