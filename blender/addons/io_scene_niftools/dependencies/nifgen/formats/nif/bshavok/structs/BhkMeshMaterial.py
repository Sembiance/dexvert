from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkMeshMaterial(BaseStruct):

	"""
	hkpBSMaterial, a subclass of hkpMeshMaterial. hkpMeshMaterial is a base class for material info for hkMeshShapes.
	"""

	__name__ = 'bhkMeshMaterial'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.material = name_type_map['SkyrimHavokMaterial'](self.context, 0, None)
		self.filter = name_type_map['HavokFilter'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'material', name_type_map['SkyrimHavokMaterial'], (0, None), (False, None), (None, None)
		yield 'filter', name_type_map['HavokFilter'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'material', name_type_map['SkyrimHavokMaterial'], (0, None), (False, None)
		yield 'filter', name_type_map['HavokFilter'], (0, None), (False, None)
