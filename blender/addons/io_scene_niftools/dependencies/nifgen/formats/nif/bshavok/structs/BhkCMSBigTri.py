from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkCMSBigTri(BaseStruct):

	"""
	Bethesda extension of hkpCompressedMeshShape::BigTriangle. Triangles that don't fit the maximum size.
	"""

	__name__ = 'bhkCMSBigTri'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.triangle = name_type_map['Triangle'](self.context, 0, None)
		self.material = name_type_map['Uint'](self.context, 0, None)
		self.welding_info = name_type_map['BhkWeldInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'triangle', name_type_map['Triangle'], (0, None), (False, None), (None, None)
		yield 'material', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'welding_info', name_type_map['BhkWeldInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'triangle', name_type_map['Triangle'], (0, None), (False, None)
		yield 'material', name_type_map['Uint'], (0, None), (False, None)
		yield 'welding_info', name_type_map['BhkWeldInfo'], (0, None), (False, None)
