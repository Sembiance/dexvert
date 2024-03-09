from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkPrismaticConstraintCInfo(BaseStruct):

	"""
	Serialization data for bhkPrismaticConstraint.
	Creates a rail between two bodies that allows translation along a single axis with linear limits and a motor.
	All three rotation axes and the remaining two translation axes are fixed.
	"""

	__name__ = 'bhkPrismaticConstraintCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Pivot.
		self.pivot_a = name_type_map['Vector4'](self.context, 0, None)

		# Rotation axis.
		self.rotation_a = name_type_map['Vector4'](self.context, 0, None)

		# Plane normal. Describes the plane the object is able to move on.
		self.plane_a = name_type_map['Vector4'](self.context, 0, None)

		# Describes the axis the object is able to travel along. Unit vector.
		self.sliding_a = name_type_map['Vector4'](self.context, 0, None)

		# Describes the axis the object is able to travel along in B coordinates. Unit vector.
		self.sliding_b = name_type_map['Vector4'](self.context, 0, None)

		# Pivot in B coordinates.
		self.pivot_b = name_type_map['Vector4'](self.context, 0, None)

		# Rotation axis.
		self.rotation_b = name_type_map['Vector4'](self.context, 0, None)

		# Plane normal. Describes the plane the object is able to move on in B coordinates.
		self.plane_b = name_type_map['Vector4'](self.context, 0, None)

		# Describes the axis the object is able to travel along. Unit vector.
		self.sliding_a = name_type_map['Vector4'](self.context, 0, None)

		# Rotation axis.
		self.rotation_a = name_type_map['Vector4'](self.context, 0, None)

		# Plane normal. Describes the plane the object is able to move on.
		self.plane_a = name_type_map['Vector4'](self.context, 0, None)

		# Pivot.
		self.pivot_a = name_type_map['Vector4'](self.context, 0, None)

		# Describes the axis the object is able to travel along in B coordinates. Unit vector.
		self.sliding_b = name_type_map['Vector4'](self.context, 0, None)

		# Rotation axis.
		self.rotation_b = name_type_map['Vector4'](self.context, 0, None)

		# Plane normal. Describes the plane the object is able to move on in B coordinates.
		self.plane_b = name_type_map['Vector4'](self.context, 0, None)

		# Pivot in B coordinates.
		self.pivot_b = name_type_map['Vector4'](self.context, 0, None)

		# Describe the min distance the object is able to travel.
		self.min_distance = name_type_map['Float'](self.context, 0, None)

		# Describe the max distance the object is able to travel.
		self.max_distance = name_type_map['Float'](self.context, 0, None)

		# Friction.
		self.friction = name_type_map['Float'](self.context, 0, None)
		self.motor = name_type_map['BhkConstraintMotorCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'rotation_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'sliding_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'sliding_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'rotation_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'sliding_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'rotation_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'sliding_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'rotation_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'min_distance', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_distance', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'motor', name_type_map['BhkConstraintMotorCInfo'], (0, None), (False, None), (lambda context: context.version >= 335675399 and not (context.bs_header.bs_version <= 16), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 335544325:
			yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'rotation_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'sliding_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'sliding_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'rotation_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None)
		if instance.context.version >= 335675399:
			yield 'sliding_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'rotation_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None)
			yield 'sliding_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'rotation_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'plane_b', name_type_map['Vector4'], (0, None), (False, None)
			yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None)
		yield 'min_distance', name_type_map['Float'], (0, None), (False, None)
		yield 'max_distance', name_type_map['Float'], (0, None), (False, None)
		yield 'friction', name_type_map['Float'], (0, None), (False, None)
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
		self.min_distance *= scale
		self.max_distance *= scale

	def update_a_b(self, transform):
		"""Update B pivot and axes from A using the given transform."""
		# pivot point
		pivot_b = ((self.context.havok_scale * self.pivot_a.get_vector_3()) * transform) / self.context.havok_scale
		self.pivot_b.x = pivot_b.x
		self.pivot_b.y = pivot_b.y
		self.pivot_b.z = pivot_b.z
		# axes (rotation only)
		transform = transform.get_matrix_33()
		sliding_b = self.sliding_a.get_vector_3() *  transform
		rotation_b = self.rotation_a.get_vector_3() *  transform
		plane_b = self.plane_a.get_vector_3() *  transform
		self.sliding_b.x = sliding_b.x
		self.sliding_b.y = sliding_b.y
		self.sliding_b.z = sliding_b.z
		self.rotation_b.x = rotation_b.x
		self.rotation_b.y = rotation_b.y
		self.rotation_b.z = rotation_b.z
		self.plane_b.x = plane_b.x
		self.plane_b.y = plane_b.y
		self.plane_b.z = plane_b.z

