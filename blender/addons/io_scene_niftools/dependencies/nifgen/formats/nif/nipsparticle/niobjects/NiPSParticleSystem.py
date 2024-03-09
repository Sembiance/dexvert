from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimesh.niobjects.NiMesh import NiMesh


class NiPSParticleSystem(NiMesh):

	"""
	Represents a particle system.
	"""

	__name__ = 'NiPSParticleSystem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.simulator = name_type_map['Ref'](self.context, 0, name_type_map['NiPSSimulator'])
		self.generator = name_type_map['Ref'](self.context, 0, name_type_map['NiPSBoundUpdater'])
		self.num_emitters = name_type_map['Uint'](self.context, 0, None)
		self.emitters = Array(self.context, 0, name_type_map['NiPSEmitter'], (0,), name_type_map['Ref'])
		self.num_spawners = name_type_map['Uint'](self.context, 0, None)
		self.spawners = Array(self.context, 0, name_type_map['NiPSSpawner'], (0,), name_type_map['Ref'])
		self.death_spawner = name_type_map['Ref'](self.context, 0, name_type_map['NiPSSpawner'])
		self.max_num_particles = name_type_map['Uint'](self.context, 0, None)
		self.has_colors = name_type_map['Bool'](self.context, 0, None)
		self.has_rotations = name_type_map['Bool'](self.context, 0, None)
		self.has_rotation_axes = name_type_map['Bool'](self.context, 0, None)
		self.has_animated_textures = name_type_map['Bool'](self.context, 0, None)
		self.world_space = name_type_map['Bool'].from_value(True)
		self.normal_method = name_type_map['AlignMethod'].ALIGN_CAMERA
		self.normal_direction = name_type_map['Vector3'](self.context, 0, None)
		self.up_method = name_type_map['AlignMethod'].ALIGN_CAMERA
		self.up_direction = name_type_map['Vector3'](self.context, 0, None)
		self.living_spawner = name_type_map['Ref'](self.context, 0, name_type_map['NiPSSpawner'])
		self.num_spawn_rate_keys = name_type_map['Byte'](self.context, 0, None)
		self.spawn_rate_keys = Array(self.context, 0, None, (0,), name_type_map['PSSpawnRateKey'])
		self.pre_rpi = name_type_map['Bool'](self.context, 0, None)
		self.dem_unknown_int = name_type_map['Uint'](self.context, 0, None)
		self.dem_unknown_byte = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'simulator', name_type_map['Ref'], (0, name_type_map['NiPSSimulator']), (False, None), (None, None)
		yield 'generator', name_type_map['Ref'], (0, name_type_map['NiPSBoundUpdater']), (False, None), (None, None)
		yield 'num_emitters', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'emitters', Array, (0, name_type_map['NiPSEmitter'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_spawners', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'spawners', Array, (0, name_type_map['NiPSSpawner'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'death_spawner', name_type_map['Ref'], (0, name_type_map['NiPSSpawner']), (False, None), (None, None)
		yield 'max_num_particles', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'has_colors', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'has_rotations', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'has_rotation_axes', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'has_animated_textures', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'world_space', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'normal_method', name_type_map['AlignMethod'], (0, None), (False, name_type_map['AlignMethod'].ALIGN_CAMERA), (lambda context: context.version >= 335937792, None)
		yield 'normal_direction', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'up_method', name_type_map['AlignMethod'], (0, None), (False, name_type_map['AlignMethod'].ALIGN_CAMERA), (lambda context: context.version >= 335937792, None)
		yield 'up_direction', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'living_spawner', name_type_map['Ref'], (0, name_type_map['NiPSSpawner']), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'num_spawn_rate_keys', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'spawn_rate_keys', Array, (0, None, (None,), name_type_map['PSSpawnRateKey']), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'pre_rpi', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335937792 and (context.user_version == 0) or ((context.version == 335938816) and (context.user_version >= 11)), None)
		yield 'dem_unknown_int', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335938816 <= context.version <= 335938816 and context.user_version >= 11, None)
		yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335938816 <= context.version <= 335938816 and context.user_version >= 11, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'simulator', name_type_map['Ref'], (0, name_type_map['NiPSSimulator']), (False, None)
		yield 'generator', name_type_map['Ref'], (0, name_type_map['NiPSBoundUpdater']), (False, None)
		yield 'num_emitters', name_type_map['Uint'], (0, None), (False, None)
		yield 'emitters', Array, (0, name_type_map['NiPSEmitter'], (instance.num_emitters,), name_type_map['Ref']), (False, None)
		yield 'num_spawners', name_type_map['Uint'], (0, None), (False, None)
		yield 'spawners', Array, (0, name_type_map['NiPSSpawner'], (instance.num_spawners,), name_type_map['Ref']), (False, None)
		yield 'death_spawner', name_type_map['Ref'], (0, name_type_map['NiPSSpawner']), (False, None)
		yield 'max_num_particles', name_type_map['Uint'], (0, None), (False, None)
		yield 'has_colors', name_type_map['Bool'], (0, None), (False, None)
		yield 'has_rotations', name_type_map['Bool'], (0, None), (False, None)
		yield 'has_rotation_axes', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335937792:
			yield 'has_animated_textures', name_type_map['Bool'], (0, None), (False, None)
		yield 'world_space', name_type_map['Bool'], (0, None), (False, True)
		if instance.context.version >= 335937792:
			yield 'normal_method', name_type_map['AlignMethod'], (0, None), (False, name_type_map['AlignMethod'].ALIGN_CAMERA)
			yield 'normal_direction', name_type_map['Vector3'], (0, None), (False, None)
			yield 'up_method', name_type_map['AlignMethod'], (0, None), (False, name_type_map['AlignMethod'].ALIGN_CAMERA)
			yield 'up_direction', name_type_map['Vector3'], (0, None), (False, None)
			yield 'living_spawner', name_type_map['Ref'], (0, name_type_map['NiPSSpawner']), (False, None)
			yield 'num_spawn_rate_keys', name_type_map['Byte'], (0, None), (False, None)
			yield 'spawn_rate_keys', Array, (0, None, (instance.num_spawn_rate_keys,), name_type_map['PSSpawnRateKey']), (False, None)
		if instance.context.version >= 335937792 and (instance.context.user_version == 0) or ((instance.context.version == 335938816) and (instance.context.user_version >= 11)):
			yield 'pre_rpi', name_type_map['Bool'], (0, None), (False, None)
		if 335938816 <= instance.context.version <= 335938816 and instance.context.user_version >= 11:
			yield 'dem_unknown_int', name_type_map['Uint'], (0, None), (False, None)
			yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None)
