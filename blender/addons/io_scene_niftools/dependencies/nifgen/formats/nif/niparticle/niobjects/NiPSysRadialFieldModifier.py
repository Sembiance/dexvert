from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysFieldModifier import NiPSysFieldModifier


class NiPSysRadialFieldModifier(NiPSysFieldModifier):

	"""
	Particle system modifier, updates the particle velocity to simulate the effects of point gravity.
	"""

	__name__ = 'NiPSysRadialFieldModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# If zero, no attenuation.
		self.radial_type = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'radial_type', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'radial_type', name_type_map['Float'], (0, None), (False, None)
