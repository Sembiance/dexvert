from nifgen.utils.inertia import getMassInertiaBox
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkConvexShape import BhkConvexShape
from nifgen.formats.nif.imports import name_type_map


class BhkBoxShape(BhkConvexShape):

	"""
	A box.
	"""

	__name__ = 'bhkBoxShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])

		# A cube stored in Half Extents. A unit cube (1.0, 1.0, 1.0) would be stored as 0.5, 0.5, 0.5.
		self.dimensions = name_type_map['Vector3'](self.context, 0, None)

		# Unused as Havok stores the Half Extents as hkVector4 with the W component unused.
		self.unused_float = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)
		yield 'dimensions', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'unused_float', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		yield 'dimensions', name_type_map['Vector3'], (0, None), (False, None)
		yield 'unused_float', name_type_map['Float'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor C{scale} on data."""
		super().apply_scale(scale)
		# apply scale on dimensions
		self.dimensions.x *= scale
		self.dimensions.y *= scale
		self.dimensions.z *= scale
		self.unused_float  *= scale

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return mass, center, and inertia tensor."""
		# the dimensions describe half the size of the box in each dimension
		# so the length of a single edge is dimension.dir * 2
		mass, inertia = getMassInertiaBox(
			(self.dimensions.x * 2, self.dimensions.y * 2, self.dimensions.z * 2),
			density = density, solid = solid)
		return mass, (0,0,0), inertia
