from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysBoundUpdateModifier(NiPSysModifier):

	"""
	Particle modifier that creates and updates bound volumes.
	"""

	__name__ = 'NiPSysBoundUpdateModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Optimize by only computing the bound of (1 / Update Skip) of the total particles each frame.
		self.update_skip = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'update_skip', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'update_skip', name_type_map['Ushort'], (0, None), (False, None)
