from nifgen.formats.nif.bshavok.niobjects.BhkPhantom import BhkPhantom


class BhkShapePhantom(BhkPhantom):

	"""
	Bethesda extension of hkpShapePhantom, a base for hkpSimpleShapePhantom and hkpCachingShapePhantom.
	"""

	__name__ = 'bhkShapePhantom'


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
