from nifgen.formats.nif.niparticle.niobjects.NiPSysVolumeEmitter import NiPSysVolumeEmitter


class BSPSysArrayEmitter(NiPSysVolumeEmitter):

	"""
	Particle emitter that uses a node, its children and subchildren to emit from.  Emission will be evenly spread along points from nodes leading to their direct parents/children only.
	"""

	__name__ = 'BSPSysArrayEmitter'


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
