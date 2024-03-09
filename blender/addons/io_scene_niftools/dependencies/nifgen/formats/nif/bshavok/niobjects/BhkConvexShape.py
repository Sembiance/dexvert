from nifgen.formats.nif.bshavok.niobjects.BhkSphereRepShape import BhkSphereRepShape
from nifgen.formats.nif.imports import name_type_map


class BhkConvexShape(BhkSphereRepShape):

	"""
	An interface that allows testing convex sets using the GJK algorithm. Also holds a radius value for creating a shell.
	"""

	__name__ = 'bhkConvexShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The radius is used to create a thin shell that is used as the shape surface.
		self.radius = name_type_map['Float'].from_value(0.05)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.05), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.05)
