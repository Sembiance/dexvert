from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysAgeDeathModifier(NiPSysModifier):

	"""
	Particle modifier that controls and updates the age of particles in the system.
	"""

	__name__ = 'NiPSysAgeDeathModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Should the particles spawn on death?
		self.spawn_on_death = name_type_map['Bool'](self.context, 0, None)

		# The spawner to use on death.
		self.spawn_modifier = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysSpawnModifier'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'spawn_on_death', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'spawn_modifier', name_type_map['Ref'], (0, name_type_map['NiPSysSpawnModifier']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'spawn_on_death', name_type_map['Bool'], (0, None), (False, None)
		yield 'spawn_modifier', name_type_map['Ref'], (0, name_type_map['NiPSysSpawnModifier']), (False, None)
