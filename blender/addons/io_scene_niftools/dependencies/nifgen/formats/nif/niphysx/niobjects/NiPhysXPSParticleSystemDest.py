from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niphysx.niobjects.NiPhysXDest import NiPhysXDest


class NiPhysXPSParticleSystemDest(NiPhysXDest):

	"""
	An object which interfaces between the PhysX scene and the Gamebryo particle system.
	"""

	__name__ = 'NiPhysXPSParticleSystemDest'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.target = name_type_map['Ptr'](self.context, 0, name_type_map['NiPSParticleSystem'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiPSParticleSystem']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiPSParticleSystem']), (False, None)
