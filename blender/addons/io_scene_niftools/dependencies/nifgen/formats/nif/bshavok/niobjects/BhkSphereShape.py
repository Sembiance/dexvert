from nifgen.utils.inertia import getMassInertiaSphere
from nifgen.formats.nif.bshavok.niobjects.BhkConvexShape import BhkConvexShape


class BhkSphereShape(BhkConvexShape):

	"""
	A sphere.
	"""

	__name__ = 'bhkSphereShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	def apply_scale(self, scale):
		"""Apply scale factor <scale> on data."""
		super().apply_scale(scale)
		# apply scale on dimensions
		self.radius *= scale

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return mass, center, and inertia tensor."""
		# the dimensions describe half the size of the box in each dimension
		# so the length of a single edge is dimension.dir * 2
		mass, inertia = getMassInertiaSphere(
			self.radius, density = density, solid = solid)
		return mass, (0,0,0), inertia

