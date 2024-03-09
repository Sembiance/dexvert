from nifgen.formats.nif.nianimation.niobjects.NiExtraDataController import NiExtraDataController


class NiColorExtraDataController(NiExtraDataController):

	"""
	Animates an NiColorExtraData object attached to an NiAVObject.
	"""

	__name__ = 'NiColorExtraDataController'


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
