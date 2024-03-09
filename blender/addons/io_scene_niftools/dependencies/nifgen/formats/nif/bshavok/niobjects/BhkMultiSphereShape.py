from nifgen.utils.inertia import getMassInertiaSphere
from nifgen.utils.mathutils import vecAdd, vecscalarMul, matAdd
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkSphereRepShape import BhkSphereRepShape
from nifgen.formats.nif.imports import name_type_map


class BhkMultiSphereShape(BhkSphereRepShape):

	"""
	A compound shape made up of spheres. This is useful as an approximation for complex shapes, as collision detection for spheres is very fast.
	However, if two bhkMultiSphereShape collide, every sphere needs to be checked against every other sphere.
	Example: 10 spheres colliding with 10 spheres will result in 100 collision checks.
	Therefore shapes like bhkCapsuleShape or bhkConvexVerticesShape should be preferred.
	"""

	__name__ = 'bhkMultiSphereShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.shape_property = name_type_map['BhkWorldObjCInfoProperty'](self.context, 0, None)
		self.num_spheres = name_type_map['Uint'].from_value(2)

		# The spheres which make up the multi sphere shape. Max of 8.
		self.spheres = Array(self.context, 0, None, (0,), name_type_map['NiBound'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shape_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None), (None, None)
		yield 'num_spheres', name_type_map['Uint'], (0, None), (False, 2), (None, None)
		yield 'spheres', Array, (0, None, (None,), name_type_map['NiBound']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shape_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None)
		yield 'num_spheres', name_type_map['Uint'], (0, None), (False, 2)
		yield 'spheres', Array, (0, None, (instance.num_spheres,), name_type_map['NiBound']), (False, None)

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return center of gravity and area."""
		subshapes_mci = [
			(mass, center, inertia)
			for (mass, inertia), center in
			zip( ( getMassInertiaSphere(radius = sphere.radius,
															 density = density, solid = solid)
					for sphere in self.spheres ),
				  ( sphere.center.as_tuple() for sphere in self.spheres ) ) ]
		total_mass = 0
		total_center = (0, 0, 0)
		total_inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
		for mass, center, inertia in subshapes_mci:
			total_mass += mass
			total_center = vecAdd(total_center,
								  vecscalarMul(center, mass / total_mass))
			total_inertia = matAdd(total_inertia, inertia)
		return total_mass, total_center, total_inertia

