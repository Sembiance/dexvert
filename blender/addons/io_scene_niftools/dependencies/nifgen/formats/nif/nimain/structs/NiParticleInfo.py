from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiParticleInfo(BaseStruct):

	"""
	Called NiPerParticleData in NiOldParticles.
	Holds the state of a particle at the time the system was saved.
	"""

	__name__ = 'NiParticleInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Particle direction and speed.
		self.velocity = name_type_map['Vector3'](self.context, 0, None)
		self.rotation_axis = name_type_map['Vector3'](self.context, 0, None)
		self.age = name_type_map['Float'](self.context, 0, None)
		self.life_span = name_type_map['Float'](self.context, 0, None)

		# Timestamp of the last update.
		self.last_update = name_type_map['Float'](self.context, 0, None)
		self.spawn_generation = name_type_map['Ushort'].from_value(0)

		# Usually matches array index
		self.code = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'velocity', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'rotation_axis', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version <= 168034305, None)
		yield 'age', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'last_update', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'spawn_generation', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'code', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'velocity', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version <= 168034305:
			yield 'rotation_axis', name_type_map['Vector3'], (0, None), (False, None)
		yield 'age', name_type_map['Float'], (0, None), (False, None)
		yield 'life_span', name_type_map['Float'], (0, None), (False, None)
		yield 'last_update', name_type_map['Float'], (0, None), (False, None)
		yield 'spawn_generation', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'code', name_type_map['Ushort'], (0, None), (False, None)
