from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiParticlesData import NiParticlesData


class NiPSysData(NiParticlesData):

	"""
	Particle system data.
	"""

	__name__ = 'NiPSysData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.particle_info = Array(self.context, 0, None, (0,), name_type_map['NiParticleInfo'])
		self.unknown_vector = name_type_map['Vector3'](self.context, 0, None)
		self.unknown_q_q_speed_byte_1 = name_type_map['Byte'](self.context, 0, None)
		self.has_rotation_speeds = name_type_map['Bool'](self.context, 0, None)
		self.rotation_speeds = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.num_added_particles = name_type_map['Ushort'](self.context, 0, None)
		self.added_particles_base = name_type_map['Ushort'](self.context, 0, None)

		# Exact position unknown, could be before Num Added Particles instead.
		self.unknown_q_q_speed_byte_2 = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'particle_info', Array, (0, None, (None,), name_type_map['NiParticleInfo']), (False, None), (lambda context: not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), None)
		yield 'unknown_vector', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'unknown_q_q_speed_byte_1', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335676423 <= context.version <= 335676423, None)
		yield 'has_rotation_speeds', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335544322, None)
		yield 'rotation_speeds', Array, (0, None, (None,), name_type_map['Float']), (False, None), (lambda context: context.version >= 335544322 and not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), True)
		yield 'num_added_particles', name_type_map['Ushort'], (0, None), (False, None), (lambda context: not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), None)
		yield 'added_particles_base', name_type_map['Ushort'], (0, None), (False, None), (lambda context: not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), None)
		yield 'unknown_q_q_speed_byte_2', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335676423 <= context.version <= 335676423, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)):
			yield 'particle_info', Array, (0, None, (instance.num_vertices,), name_type_map['NiParticleInfo']), (False, None)
		if instance.context.bs_header.bs_version == 155:
			yield 'unknown_vector', name_type_map['Vector3'], (0, None), (False, None)
		if 335676423 <= instance.context.version <= 335676423:
			yield 'unknown_q_q_speed_byte_1', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.version >= 335544322:
			yield 'has_rotation_speeds', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335544322 and not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)) and instance.has_rotation_speeds:
			yield 'rotation_speeds', Array, (0, None, (instance.num_vertices,), name_type_map['Float']), (False, None)
		if not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)):
			yield 'num_added_particles', name_type_map['Ushort'], (0, None), (False, None)
			yield 'added_particles_base', name_type_map['Ushort'], (0, None), (False, None)
		if 335676423 <= instance.context.version <= 335676423:
			yield 'unknown_q_q_speed_byte_2', name_type_map['Byte'], (0, None), (False, None)
