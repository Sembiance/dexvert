from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleModifier import NiParticleModifier


class NiParticleColorModifier(NiParticleModifier):

	"""
	LEGACY (pre-10.1) particle modifier.
	"""

	__name__ = 'NiParticleColorModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.color_data = name_type_map['Ref'](self.context, 0, name_type_map['NiColorData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'color_data', name_type_map['Ref'], (0, name_type_map['NiColorData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'color_data', name_type_map['Ref'], (0, name_type_map['NiColorData']), (False, None)
