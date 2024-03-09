from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiGeometryData import NiGeometryData


class NiParticlesData(NiGeometryData):

	"""
	Generic rotating particles data object.
	Bethesda 20.2.0.7 NIFs: NiParticlesData no longer inherits from NiGeometryData and inherits NiObject directly.
	"""

	__name__ = 'NiParticlesData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The maximum number of particles (matches the number of vertices).
		self.num_particles = name_type_map['Ushort'](self.context, 0, None)

		# The particles' size.
		self.particle_radius = name_type_map['Float'](self.context, 0, None)

		# Is the particle size array present?
		self.has_radii = name_type_map['Bool'](self.context, 0, None)

		# The individual particle sizes.
		self.radii = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# The number of active particles at the time the system was saved. This is also the number of valid entries in the following arrays.
		self.num_active = name_type_map['Ushort'](self.context, 0, None)

		# Is the particle size array present?
		self.has_sizes = name_type_map['Bool'](self.context, 0, None)

		# The individual particle sizes.
		self.sizes = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# Is the particle rotation array present?
		self.has_rotations = name_type_map['Bool'](self.context, 0, None)

		# The individual particle rotations.
		self.rotations = Array(self.context, 0, None, (0,), name_type_map['Quaternion'])

		# Are the angles of rotation present?
		self.has_rotation_angles = name_type_map['Bool'](self.context, 0, None)

		# Angles of rotation
		self.rotation_angles = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# Are axes of rotation present?
		self.has_rotation_axes = name_type_map['Bool'](self.context, 0, None)

		# Axes of rotation.
		self.rotation_axes = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.has_texture_indices = name_type_map['Bool'](self.context, 0, None)

		# How many quads to use in BSPSysSubTexModifier for texture atlasing

		# 2,4,8,16,32,64 are potential values. If "Has" was no then this should be 256, which represents a 16x16 framed image, which is invalid
		self.num_subtexture_offsets = name_type_map['Byte'](self.context, 0, None)

		# Defines UV offsets
		self.subtexture_offsets = Array(self.context, 0, None, (0,), name_type_map['Vector4'])

		# Sets aspect ratio for Subtexture Offset UV quads
		self.aspect_ratio = name_type_map['Float'](self.context, 0, None)
		self.aspect_flags = name_type_map['AspectFlags'](self.context, 0, None)
		self.speed_to_aspect_aspect_2 = name_type_map['Float'](self.context, 0, None)
		self.speed_to_aspect_speed_1 = name_type_map['Float'](self.context, 0, None)
		self.speed_to_aspect_speed_2 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_particles', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 67108866, None)
		yield 'particle_radius', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 167772416, None)
		yield 'has_radii', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'radii', Array, (0, None, (None,), name_type_map['Float']), (False, None), (lambda context: context.version >= 167837696 and not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), True)
		yield 'num_active', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'has_sizes', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'sizes', Array, (0, None, (None,), name_type_map['Float']), (False, None), (lambda context: not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), True)
		yield 'has_rotations', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167772416, None)
		yield 'rotations', Array, (0, None, (None,), name_type_map['Quaternion']), (False, None), (lambda context: context.version >= 167772416 and not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), True)
		yield 'has_rotation_angles', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335544324, None)
		yield 'rotation_angles', Array, (0, None, (None,), name_type_map['Float']), (False, None), (lambda context: not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), True)
		yield 'has_rotation_axes', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335544324, None)
		yield 'rotation_axes', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (lambda context: context.version >= 335544324 and not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), True)
		yield 'has_texture_indices', name_type_map['Bool'], (0, None), (False, None), (lambda context: (context.version == 335675399) and (context.bs_header.bs_version > 0), None)
		yield 'num_subtexture_offsets', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'num_subtexture_offsets', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and (context.bs_header.bs_version > 0) and (context.bs_header.bs_version <= 34), None)
		yield 'subtexture_offsets', Array, (0, None, (None,), name_type_map['Vector4']), (False, None), (lambda context: (context.version == 335675399) and (context.bs_header.bs_version > 0), None)
		yield 'aspect_ratio', name_type_map['Float'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'aspect_flags', name_type_map['AspectFlags'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'speed_to_aspect_aspect_2', name_type_map['Float'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'speed_to_aspect_speed_1', name_type_map['Float'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'speed_to_aspect_speed_2', name_type_map['Float'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 67108866:
			yield 'num_particles', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 167772416:
			yield 'particle_radius', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 167837696:
			yield 'has_radii', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 167837696 and not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)) and instance.has_radii:
			yield 'radii', Array, (0, None, (instance.num_vertices,), name_type_map['Float']), (False, None)
		yield 'num_active', name_type_map['Ushort'], (0, None), (False, None)
		yield 'has_sizes', name_type_map['Bool'], (0, None), (False, None)
		if not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)) and instance.has_sizes:
			yield 'sizes', Array, (0, None, (instance.num_vertices,), name_type_map['Float']), (False, None)
		if instance.context.version >= 167772416:
			yield 'has_rotations', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 167772416 and not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)) and instance.has_rotations:
			yield 'rotations', Array, (0, None, (instance.num_vertices,), name_type_map['Quaternion']), (False, None)
		if instance.context.version >= 335544324:
			yield 'has_rotation_angles', name_type_map['Bool'], (0, None), (False, None)
		if not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)) and instance.has_rotation_angles:
			yield 'rotation_angles', Array, (0, None, (instance.num_vertices,), name_type_map['Float']), (False, None)
		if instance.context.version >= 335544324:
			yield 'has_rotation_axes', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335544324 and not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)) and instance.has_rotation_axes:
			yield 'rotation_axes', Array, (0, None, (instance.num_vertices,), name_type_map['Vector3']), (False, None)
		if (instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0):
			yield 'has_texture_indices', name_type_map['Bool'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version > 34:
			yield 'num_subtexture_offsets', name_type_map['Uint'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and (instance.context.bs_header.bs_version > 0) and (instance.context.bs_header.bs_version <= 34):
			yield 'num_subtexture_offsets', name_type_map['Byte'], (0, None), (False, None)
		if (instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0):
			yield 'subtexture_offsets', Array, (0, None, (instance.num_subtexture_offsets,), name_type_map['Vector4']), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version > 34:
			yield 'aspect_ratio', name_type_map['Float'], (0, None), (False, None)
			yield 'aspect_flags', name_type_map['AspectFlags'], (0, None), (False, None)
			yield 'speed_to_aspect_aspect_2', name_type_map['Float'], (0, None), (False, None)
			yield 'speed_to_aspect_speed_1', name_type_map['Float'], (0, None), (False, None)
			yield 'speed_to_aspect_speed_2', name_type_map['Float'], (0, None), (False, None)
