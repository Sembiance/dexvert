from nifgen.utils.inertia import getMassInertiaCapsule
import nifgen.utils.mathutils as m_util
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkConvexShape import BhkConvexShape
from nifgen.formats.nif.imports import name_type_map


class BhkCapsuleShape(BhkConvexShape):

	"""
	A capsule.
	"""

	__name__ = 'bhkCapsuleShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])

		# First point on the capsule's axis.
		self.first_point = name_type_map['Vector3'](self.context, 0, None)

		# Matches first capsule radius.
		self.radius_1 = name_type_map['Float'](self.context, 0, None)

		# Second point on the capsule's axis.
		self.second_point = name_type_map['Vector3'](self.context, 0, None)

		# Matches second capsule radius.
		self.radius_2 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)
		yield 'first_point', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'radius_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'second_point', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'radius_2', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		yield 'first_point', name_type_map['Vector3'], (0, None), (False, None)
		yield 'radius_1', name_type_map['Float'], (0, None), (False, None)
		yield 'second_point', name_type_map['Vector3'], (0, None), (False, None)
		yield 'radius_2', name_type_map['Float'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor <scale> on data."""
		super().apply_scale(scale)
		# apply scale on dimensions
		self.radius *= scale
		self.radius_1 *= scale
		self.radius_2 *= scale
		self.first_point.x *= scale
		self.first_point.y *= scale
		self.first_point.z *= scale
		self.second_point.x *= scale
		self.second_point.y *= scale
		self.second_point.z *= scale

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return mass, center, and inertia tensor."""
		# (assumes self.radius == self.radius_1 == self.radius_2)
		length = (self.first_point - self.second_point).norm()
		mass, inertia = getMassInertiaCapsule(
			radius = self.radius, length = length,
			density = density, solid = solid)
		# now fix inertia so it is expressed in the right coordinates
		# need a transform that maps (0,0,length/2) on (second - first) / 2
		# and (0,0,-length/2) on (first - second)/2
		vec1 = ((self.second_point - self.first_point) / length).as_tuple()
		# find an orthogonal vector to vec1
		index = min(enumerate(vec1), key=lambda val: abs(val[1]))[0]
		vec2 = m_util.vecCrossProduct(vec1, tuple((1 if i == index else 0)
										   for i in range(3)))
		vec2 = m_util.vecscalarMul(vec2, 1/m_util.vecNorm(vec2))
		# find an orthogonal vector to vec1 and vec2
		vec3 = m_util.vecCrossProduct(vec1, vec2)
		# get transform matrix
		transform_transposed = (vec2, vec3, vec1) # this is effectively the transposed of our transform
		transform = m_util.matTransposed(transform_transposed)
		# check the result (debug)
		assert(m_util.vecDistance(m_util.matvecMul(transform, (0,0,1)), vec1) < 0.0001)
		assert(abs(m_util.matDeterminant(transform) - 1) < 0.0001)
		# transform the inertia tensor
		inertia = m_util.matMul(m_util.matMul(transform_transposed, inertia), transform)
		return (mass,
				((self.first_point + self.second_point) * 0.5).as_tuple(),
				inertia)
