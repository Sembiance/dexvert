from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSSimulatorStep import NiPSSimulatorStep


class NiPSSimulatorGeneralStep(NiPSSimulatorStep):

	"""
	Encapsulates a floodgate kernel that updates particle size, colors, and rotations.
	"""

	__name__ = 'NiPSSimulatorGeneralStep'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_size_keys = name_type_map['Byte'](self.context, 0, None)

		# The particle size keys.
		self.size_keys = Array(self.context, 1, name_type_map['Float'], (0,), name_type_map['Key'])

		# The loop behavior for the size keys.
		self.size_loop_behavior = name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE
		self.num_color_keys = name_type_map['Byte'](self.context, 0, None)

		# The particle color keys.
		self.color_keys = Array(self.context, 1, name_type_map['ByteColor4'], (0,), name_type_map['Key'])

		# The loop behavior for the color keys.
		self.color_loop_behavior = name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE
		self.num_rotation_keys = name_type_map['Byte'](self.context, 0, None)

		# The particle rotation keys.
		self.rotation_keys = Array(self.context, 1, name_type_map['Quaternion'], (0,), name_type_map['QuatKey'])

		# The loop behavior for the rotation keys.
		self.rotation_loop_behavior = name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE

		# The the amount of time over which a particle's size is ramped from 0.0 to 1.0 in seconds
		self.grow_time = name_type_map['Float'](self.context, 0, None)

		# The the amount of time over which a particle's size is ramped from 1.0 to 0.0 in seconds
		self.shrink_time = name_type_map['Float'](self.context, 0, None)

		# Specifies the particle generation to which the grow effect should be applied. This is usually generation 0, so that newly created particles will grow.
		self.grow_generation = name_type_map['Ushort'](self.context, 0, None)

		# Specifies the particle generation to which the shrink effect should be applied. This is usually the highest supported generation for the particle system, so that particles will shrink immediately before getting killed.
		self.shrink_generation = name_type_map['Ushort'](self.context, 0, None)
		self.dem_unknown_byte = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_size_keys', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'size_keys', Array, (1, name_type_map['Float'], (None,), name_type_map['Key']), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'size_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE), (lambda context: context.version >= 335937792, None)
		yield 'num_color_keys', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'color_keys', Array, (1, name_type_map['ByteColor4'], (None,), name_type_map['Key']), (False, None), (None, None)
		yield 'color_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE), (lambda context: context.version >= 335937792, None)
		yield 'num_rotation_keys', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'rotation_keys', Array, (1, name_type_map['Quaternion'], (None,), name_type_map['QuatKey']), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'rotation_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE), (lambda context: context.version >= 335937792, None)
		yield 'grow_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'shrink_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'grow_generation', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'shrink_generation', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335938816 <= context.version <= 335938816 and context.user_version >= 14, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 335937792:
			yield 'num_size_keys', name_type_map['Byte'], (0, None), (False, None)
			yield 'size_keys', Array, (1, name_type_map['Float'], (instance.num_size_keys,), name_type_map['Key']), (False, None)
			yield 'size_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE)
		yield 'num_color_keys', name_type_map['Byte'], (0, None), (False, None)
		yield 'color_keys', Array, (1, name_type_map['ByteColor4'], (instance.num_color_keys,), name_type_map['Key']), (False, None)
		if instance.context.version >= 335937792:
			yield 'color_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE)
			yield 'num_rotation_keys', name_type_map['Byte'], (0, None), (False, None)
			yield 'rotation_keys', Array, (1, name_type_map['Quaternion'], (instance.num_rotation_keys,), name_type_map['QuatKey']), (False, None)
			yield 'rotation_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, name_type_map['PSLoopBehavior'].PS_LOOP_AGESCALE)
		yield 'grow_time', name_type_map['Float'], (0, None), (False, None)
		yield 'shrink_time', name_type_map['Float'], (0, None), (False, None)
		yield 'grow_generation', name_type_map['Ushort'], (0, None), (False, None)
		yield 'shrink_generation', name_type_map['Ushort'], (0, None), (False, None)
		if 335938816 <= instance.context.version <= 335938816 and instance.context.user_version >= 14:
			yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None)
