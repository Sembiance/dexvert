from nifgen.formats.nif.bshavok.niobjects.BhkSerializable import BhkSerializable


class BhkShape(BhkSerializable):

	"""
	The base class for narrowphase collision detection objects.
	All narrowphase collision detection is performed between pairs of bhkShape objects by creating appropriate collision agents.
	"""

	__name__ = 'bhkShape'


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
