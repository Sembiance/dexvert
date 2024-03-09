from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleModifier import NiParticleModifier


class NiParticleGrowFade(NiParticleModifier):

	"""
	LEGACY (pre-10.1) particle modifier.
	"""

	__name__ = 'NiParticleGrowFade'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The time from the beginning of the particle lifetime during which the particle grows.
		self.grow = name_type_map['Float'](self.context, 0, None)

		# The time from the end of the particle lifetime during which the particle fades.
		self.fade = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'grow', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'fade', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'grow', name_type_map['Float'], (0, None), (False, None)
		yield 'fade', name_type_map['Float'], (0, None), (False, None)
