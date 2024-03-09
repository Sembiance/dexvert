from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysPartSpawnModifier(NiPSysModifier):

	"""
	WorldShift-specific Particle Spawn modifier
	"""

	__name__ = 'NiPSysPartSpawnModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.particles_per_second = name_type_map['Float'].from_value(40.0)

		# Default of FLT_MIN would indicate End Time but it seems more like Frequency/Tick Rate or Start Time.
		self.time = name_type_map['Float'].from_value(-3.402823466e+38)
		self.spawner = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysSpawnModifier'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'particles_per_second', name_type_map['Float'], (0, None), (False, 40.0), (None, None)
		yield 'time', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (None, None)
		yield 'spawner', name_type_map['Ref'], (0, name_type_map['NiPSysSpawnModifier']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'particles_per_second', name_type_map['Float'], (0, None), (False, 40.0)
		yield 'time', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
		yield 'spawner', name_type_map['Ref'], (0, name_type_map['NiPSysSpawnModifier']), (False, None)
