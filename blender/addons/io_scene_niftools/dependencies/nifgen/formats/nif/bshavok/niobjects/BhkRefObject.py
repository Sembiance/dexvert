from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BhkRefObject(NiObject):

	"""
	Bethesda extension of hkReferencedObject, the base for all classes in the Havok SDK.
	"""

	__name__ = 'bhkRefObject'


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

	def get_shape_mass_center_inertia(self, density=1, solid=True):
		"""Return mass, center of gravity, and inertia tensor of
		this object's shape, if self.shape is not None.

		If self.shape is None, then returns zeros for everything.
		"""
		if not self.shape:
			mass = 0
			center = (0, 0, 0)
			inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
		else:
			mass, center, inertia = self.shape.get_mass_center_inertia(
				density=density, solid=solid)
		return mass, center, inertia

