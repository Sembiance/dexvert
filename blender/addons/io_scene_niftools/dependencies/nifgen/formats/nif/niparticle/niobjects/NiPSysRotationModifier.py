from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysRotationModifier(NiPSysModifier):

	"""
	Particle modifier that adds rotations to particles.
	"""

	__name__ = 'NiPSysRotationModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Initial Rotation Speed in radians per second.
		self.rotation_speed = name_type_map['Float'](self.context, 0, None)

		# Distributes rotation speed over the range [Speed - Variation, Speed + Variation].
		self.rotation_speed_variation = name_type_map['Float'](self.context, 0, None)
		self.unknown_vector = name_type_map['Vector4'](self.context, 0, None)
		self.unknown_byte = name_type_map['Byte'](self.context, 0, None)

		# Initial Rotation Angle in radians.
		self.rotation_angle = name_type_map['Float'](self.context, 0, None)

		# Distributes rotation angle over the range [Angle - Variation, Angle + Variation].
		self.rotation_angle_variation = name_type_map['Float'](self.context, 0, None)

		# Randomly negate the initial rotation speed?
		self.random_rot_speed_sign = name_type_map['Bool'](self.context, 0, None)

		# Assign a random axis to new particles?
		self.random_axis = name_type_map['Bool'].from_value(True)

		# Initial rotation axis.
		self.axis = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'rotation_speed', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'rotation_speed_variation', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335544322, None)
		yield 'unknown_vector', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'unknown_byte', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'rotation_angle', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335544322, None)
		yield 'rotation_angle_variation', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335544322, None)
		yield 'random_rot_speed_sign', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335544322, None)
		yield 'random_axis', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'rotation_speed', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335544322:
			yield 'rotation_speed_variation', name_type_map['Float'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155:
			yield 'unknown_vector', name_type_map['Vector4'], (0, None), (False, None)
			yield 'unknown_byte', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.version >= 335544322:
			yield 'rotation_angle', name_type_map['Float'], (0, None), (False, None)
			yield 'rotation_angle_variation', name_type_map['Float'], (0, None), (False, None)
			yield 'random_rot_speed_sign', name_type_map['Bool'], (0, None), (False, None)
		yield 'random_axis', name_type_map['Bool'], (0, None), (False, True)
		yield 'axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
