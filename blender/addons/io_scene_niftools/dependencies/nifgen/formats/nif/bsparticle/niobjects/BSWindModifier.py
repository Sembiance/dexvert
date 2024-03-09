from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSWindModifier(NiPSysModifier):

	"""
	Particle Modifier that uses the wind value from the gamedata to alter the path of particles.
	"""

	__name__ = 'BSWindModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The amount of force wind will have on particles.
		self.strength = name_type_map['Float'].from_value(0.25)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'strength', name_type_map['Float'], (0, None), (False, 0.25), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'strength', name_type_map['Float'], (0, None), (False, 0.25)
