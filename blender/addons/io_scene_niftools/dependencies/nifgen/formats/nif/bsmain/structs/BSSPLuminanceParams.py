from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSSPLuminanceParams(BaseStruct):

	__name__ = 'BSSPLuminanceParams'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.lum_emittance = name_type_map['Float'].from_value(100.0)
		self.exposure_offset = name_type_map['Float'].from_value(13.5)
		self.final_exposure_min = name_type_map['Float'].from_value(2.0)
		self.final_exposure_max = name_type_map['Float'].from_value(3.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lum_emittance', name_type_map['Float'], (0, None), (False, 100.0), (None, None)
		yield 'exposure_offset', name_type_map['Float'], (0, None), (False, 13.5), (None, None)
		yield 'final_exposure_min', name_type_map['Float'], (0, None), (False, 2.0), (None, None)
		yield 'final_exposure_max', name_type_map['Float'], (0, None), (False, 3.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lum_emittance', name_type_map['Float'], (0, None), (False, 100.0)
		yield 'exposure_offset', name_type_map['Float'], (0, None), (False, 13.5)
		yield 'final_exposure_min', name_type_map['Float'], (0, None), (False, 2.0)
		yield 'final_exposure_max', name_type_map['Float'], (0, None), (False, 3.0)
