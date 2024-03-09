from nifgen.formats.nif.bshavok.niobjects.BhkWorldObject import BhkWorldObject


class BhkPhantom(BhkWorldObject):

	"""
	Bethesda extension of hkpPhantom. A Phantom is the core non-physical object in the system.
	Receives events when an overlap with another phantom or an entity begins or ends.
	"""

	__name__ = 'bhkPhantom'


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
