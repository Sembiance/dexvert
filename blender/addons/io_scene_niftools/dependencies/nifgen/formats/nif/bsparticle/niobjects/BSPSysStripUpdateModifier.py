from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSPSysStripUpdateModifier(NiPSysModifier):

	"""
	Bethesda-Specific (mesh?) Particle System Modifier.
	"""

	__name__ = 'BSPSysStripUpdateModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.update_delta_time = name_type_map['Float'].from_value(0.033333)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'update_delta_time', name_type_map['Float'], (0, None), (False, 0.033333), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'update_delta_time', name_type_map['Float'], (0, None), (False, 0.033333)
