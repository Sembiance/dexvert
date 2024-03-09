from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysFieldModifier import NiPSysFieldModifier


class NiPSysTurbulenceFieldModifier(NiPSysFieldModifier):

	"""
	Particle system modifier, implements a turbulence field force for particles.
	"""

	__name__ = 'NiPSysTurbulenceFieldModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# How many turbulence updates per second.
		self.frequency = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'frequency', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'frequency', name_type_map['Float'], (0, None), (False, None)
