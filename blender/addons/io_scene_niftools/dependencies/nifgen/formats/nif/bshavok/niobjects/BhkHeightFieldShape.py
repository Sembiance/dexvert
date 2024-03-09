from nifgen.formats.nif.bshavok.niobjects.BhkShape import BhkShape
from nifgen.formats.nif.imports import name_type_map


class BhkHeightFieldShape(BhkShape):

	"""
	An interface for a shape which can collide with an array of spheres.
	"""

	__name__ = 'bhkHeightFieldShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The material of the shape.
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
