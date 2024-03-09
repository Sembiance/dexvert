from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class SkinInfoSet(BaseStruct):

	"""
	A set of NiBoneLODController::SkinInfo.
	"""

	__name__ = 'SkinInfoSet'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_skin_info = name_type_map['Uint'](self.context, 0, None)
		self.skin_info = Array(self.context, 0, None, (0,), name_type_map['SkinInfo'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_skin_info', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'skin_info', Array, (0, None, (None,), name_type_map['SkinInfo']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_skin_info', name_type_map['Uint'], (0, None), (False, None)
		yield 'skin_info', Array, (0, None, (instance.num_skin_info,), name_type_map['SkinInfo']), (False, None)
