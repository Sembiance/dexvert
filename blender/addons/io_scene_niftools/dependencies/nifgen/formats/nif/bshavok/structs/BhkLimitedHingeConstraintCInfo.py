from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkLimitedHingeConstraintCInfo(BaseStruct):

	"""
	Serialization data for bhkLimitedHingeConstraint.
	This constraint allows rotation about a specified axis, limited by specified boundaries.
	"""

	__name__ = 'bhkLimitedHingeConstraintCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Pivot point around which the object will rotate.
		self.pivot_a = name_type_map['Vector4'](self.context, 0, None)

		# Axis of rotation.
		self.axis_a = name_type_map['Vector4'](self.context, 0, None)

		# Vector in the rotation plane which defines the zero angle.
		self.perp_axis_in_a_1 = name_type_map['Vector4'](self.context, 0, None)

		# Vector in the rotation plane, orthogonal on the previous one, which defines the positive direction of rotation. This is always the vector product of Axis A and Perp Axis In A1.
		self.perp_axis_in_a_2 = name_type_map['Vector4'](self.context, 0, None)

		# Pivot A in second entity coordinate system.
		self.pivot_b = name_type_map['Vector4'](self.context, 0, None)

		# Axis A in second entity coordinate system.
		self.axis_b = name_type_map['Vector4'](self.context, 0, None)

		# Perp Axis In A2 in second entity coordinate system.
		self.perp_axis_in_b_2 = name_type_map['Vector4'](self.context, 0, None)

		# Axis of rotation.
		self.axis_a = name_type_map['Vector4'](self.context, 0, None)

		# Vector in the rotation plane which defines the zero angle.
		self.perp_axis_in_a_1 = name_type_map['Vector4'](self.context, 0, None)

		# Vector in the rotation plane, orthogonal on the previous one, which defines the positive direction of rotation. This is always the vector product of Axis A and Perp Axis In A1.
		self.perp_axis_in_a_2 = name_type_map['Vector4'](self.context, 0, None)

		# Pivot point around which the object will rotate.
		self.pivot_a = name_type_map['Vector4'](self.context, 0, None)

		# Axis A in second entity coordinate system.
		self.axis_b = name_type_map['Vector4'](self.context, 0, None)

		# Perp Axis In A1 in second entity coordinate system.
		self.perp_axis_in_b_1 = name_type_map['Vector4'](self.context, 0, None)

		# Perp Axis In A2 in second entity coordinate system.
		self.perp_axis_in_b_2 = name_type_map['Vector4'](self.context, 0, None)

		# Pivot A in second entity coordinate system.
		self.pivot_b = name_type_map['Vector4'](self.context, 0, None)

		# Minimum rotation angle.
		self.min_angle = name_type_map['Float'](self.context, 0, None)

		# Maximum rotation angle.
		self.max_angle = name_type_map['Float'](self.context, 0, None)

		# Maximum friction, typically either 0 or 10. In Fallout 3, typically 100.
		self.max_friction = name_type_map['Float'](self.context, 0, None)
		self.motor = name_type_map['BhkConstraintMotorCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'axis_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'perp_axis_in_a_1', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'perp_axis_in_a_2', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'axis_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'perp_axis_in_b_2', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'axis_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'perp_axis_in_a_1', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'perp_axis_in_a_2', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'axis_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'perp_axis_in_b_1', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'perp_axis_in_b_2', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'min_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'motor', name_type_map['BhkConstraintMotorCInfo'], (0, None), (False, None), (lambda context: context.version >= 335675399 and not (context.bs_header.bs_version <= 16), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version <= 16:
			yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'axis_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'perp_axis_in_a_1', name_type_map['Vector4'], (0, None), (False, None)
			yield 'perp_axis_in_a_2', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'axis_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'perp_axis_in_b_2', name_type_map['Vector4'], (0, None), (False, None)
		if not (instance.context.bs_header.bs_version <= 16):
			yield 'axis_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'perp_axis_in_a_1', name_type_map['Vector4'], (0, None), (False, None)
			yield 'perp_axis_in_a_2', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'axis_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'perp_axis_in_b_1', name_type_map['Vector4'], (0, None), (False, None)
			yield 'perp_axis_in_b_2', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None)
		yield 'min_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'max_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'max_friction', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335675399 and not (instance.context.bs_header.bs_version <= 16):
			yield 'motor', name_type_map['BhkConstraintMotorCInfo'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Scale data."""
		# apply scale on transform
		self.pivot_a.x *= scale
		self.pivot_a.y *= scale
		self.pivot_a.z *= scale
		self.pivot_b.x *= scale
		self.pivot_b.y *= scale
		self.pivot_b.z *= scale

	def update_a_b(self, transform):
		"""Update B pivot and axes from A using the given transform."""
		# pivot point
		pivot_b = ((self.context.havok_scale * self.pivot_a.get_vector_3()) * transform) / self.context.havok_scale
		self.pivot_b.x = pivot_b.x
		self.pivot_b.y = pivot_b.y
		self.pivot_b.z = pivot_b.z
		# axes (rotation only)
		transform = transform.get_matrix_33()
		axis_b = self.axis_a.get_vector_3() *  transform
		perp_axis_in_b_1 = self.perp_axis_in_a_1.get_vector_3() * transform
		perp_axis_in_b_2 = self.perp_axis_in_a_2.get_vector_3() * transform
		self.axis_b.x = axis_b.x
		self.axis_b.y = axis_b.y
		self.axis_b.z = axis_b.z
		self.perp_axis_in_b_1.x = perp_axis_in_b_1.x
		self.perp_axis_in_b_1.y = perp_axis_in_b_1.y
		self.perp_axis_in_b_1.z = perp_axis_in_b_1.z
		self.perp_axis_in_b_2.x = perp_axis_in_b_2.x
		self.perp_axis_in_b_2.y = perp_axis_in_b_2.y
		self.perp_axis_in_b_2.z = perp_axis_in_b_2.z

