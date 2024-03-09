from nifgen.formats.nif.bshavok.niobjects.BhkWorldObject import BhkWorldObject
from nifgen.formats.nif.imports import name_type_map


class BhkEntity(BhkWorldObject):

	"""
	Bethesda extension of hkpEntity. An Entity is the core physical object in the system.
	"""

	__name__ = 'bhkEntity'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.entity_info = name_type_map['BhkEntityCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'entity_info', name_type_map['BhkEntityCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'entity_info', name_type_map['BhkEntityCInfo'], (0, None), (False, None)
