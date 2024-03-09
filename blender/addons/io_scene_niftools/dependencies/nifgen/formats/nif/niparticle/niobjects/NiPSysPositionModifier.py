from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysPositionModifier(NiPSysModifier):

	"""
	Particle modifier that updates the particle positions based on velocity and last update time.
	"""

	__name__ = 'NiPSysPositionModifier'


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
