from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkRagdollConstraintCInfo(BaseStruct):

	"""
	Serialization data for bhkRagdollConstraint.
	The area of movement can be represented as a main cone + 2 orthogonal cones which may subtract from the main cone volume depending on limits.
	"""

	__name__ = 'bhkRagdollConstraintCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The point where the constraint is attached to its parent rigidbody.
		self.pivot_a = name_type_map['Vector4'](self.context, 0, None)

		# Defines the orthogonal plane in which the body can move, the orthogonal directions in which the shape can be controlled (the direction orthogonal on this one and Twist A).
		self.plane_a = name_type_map['Vector4'](self.context, 0, None)

		# Central directed axis of the cone in which the object can rotate. Orthogonal on Plane A.
		self.twist_a = name_type_map['Vector4'](self.context, 0, None)

		# The point where the constraint is attached to the other rigidbody.
		self.pivot_b = name_type_map['Vector4'](self.context, 0, None)

		# Defines the orthogonal plane in which the shape can be controlled (the direction orthogonal on this one and Twist B).
		self.plane_b = name_type_map['Vector4'](self.context, 0, None)

		# Central directed axis of the cone in which the object can rotate. Orthogonal on Plane B.
		self.twist_b = name_type_map['Vector4'](self.context, 0, None)

		# Central directed axis of the cone in which the object can rotate. Orthogonal on Plane A.
		self.twist_a = name_type_map['Vector4'](self.context, 0, None)

		# Defines the orthogonal plane in which the body can move, the orthogonal directions in which the shape can be controlled (the direction orthogonal on this one and Twist A).
		self.plane_a = name_type_map['Vector4'](self.context, 0, None)

		# Defines the orthogonal directions in which the shape can be controlled (namely in this direction, and in the direction orthogonal on this one and Twist A).
		self.motor_a = name_type_map['Vector4'](self.context, 0, None)

		# Point around which the object will rotate. Defines the orthogonal directions in which the shape can be controlled (namely in this direction, and in the direction orthogonal on this one and Twist A).
		self.pivot_a = name_type_map['Vector4'](self.context, 0, None)

		# Central directed axis of the cone in which the object can rotate. Orthogonal on Plane B.
		self.twist_b = name_type_map['Vector4'](self.context, 0, None)

		# Defines the orthogonal plane in which the body can move, the orthogonal directions in which the shape can be controlled (the direction orthogonal on this one and Twist A).
		self.plane_b = name_type_map['Vector4'](self.context, 0, None)

		# Defines the orthogonal directions in which the shape can be controlled (namely in this direction, and in the direction orthogonal on this one and Twist A).
		self.motor_b = name_type_map['Vector4'](self.context, 0, None)

		# Defines the orthogonal directions in which the shape can be controlled (namely in this direction, and in the direction orthogonal on this one and Twist A).
		self.pivot_b = name_type_map['Vector4'](self.context, 0, None)

		# Maximum angle the object can rotate around the vector orthogonal on Plane A and Twist A relative to the Twist A vector. Note that Cone Min Angle is not stored, but is simply minus this angle.
		self.cone_max_angle = name_type_map['Float'](self.context, 0, None)

		# Minimum angle the object can rotate around Plane A, relative to Twist A.
		self.plane_min_angle = name_type_map['Float'](self.context, 0, None)

		# Maximum angle the object can rotate around Plane A, relative to Twist A.
		self.plane_max_angle = name_type_map['Float'](self.context, 0, None)

		# Minimum angle the object can rotate around Twist A, relative to Plane A.
		self.twist_min_angle = name_type_map['Float'](self.context, 0, None)

		# Maximum angle the object can rotate around Twist A, relative to Plane A.
		self.twist_max_angle = name_type_map['Float'](self.context, 0, None)

		# Maximum friction, typically 0 or 10. In Fallout 3, typically 100.
		self.max_friction = name_type_map['Float'](self.context, 0, None)
		self.motor = name_type_map['BhkConstraintMotorCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'twist_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'twist_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 16, None)
		yield 'twist_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'motor_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'twist_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'motor_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: not (context.bs_header.bs_version <= 16), None)
		yield 'cone_max_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'plane_min_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'plane_max_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'twist_min_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'twist_max_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'motor', name_type_map['BhkConstraintMotorCInfo'], (0, None), (False, None), (lambda context: context.version >= 335675399 and not (context.bs_header.bs_version <= 16), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version <= 16:
			yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'twist_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'twist_b', name_type_map['Vector4'], (0, None), (False, None)
		if not (instance.context.bs_header.bs_version <= 16):
			yield 'twist_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'motor_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'twist_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'motor_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None)
		yield 'cone_max_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'plane_min_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'plane_max_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'twist_min_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'twist_max_angle', name_type_map['Float'], (0, None), (False, None)
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
		plane_b = self.plane_a.get_vector_3() *  transform
		twist_b = self.twist_a.get_vector_3() *  transform
		self.plane_b.x = plane_b.x
		self.plane_b.y = plane_b.y
		self.plane_b.z = plane_b.z
		self.twist_b.x = twist_b.x
		self.twist_b.y = twist_b.y
		self.twist_b.z = twist_b.z

