from nifgen.base_struct import BaseStruct
from nifgen.formats.dds.imports import name_type_map


class Dxt10Header(BaseStruct):

	__name__ = 'DXT10Header'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dxgi_format = name_type_map['DxgiFormat'](self.context, 0, None)
		self.resource_dimension = name_type_map['D3D10ResourceDimension'](self.context, 0, None)
		self.misc_flag = name_type_map['Uint'](self.context, 0, None)
		self.num_tiles = name_type_map['Uint'].from_value(1)
		self.misc_flag_2 = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dxgi_format', name_type_map['DxgiFormat'], (0, None), (False, None), (None, None)
		yield 'resource_dimension', name_type_map['D3D10ResourceDimension'], (0, None), (False, None), (None, None)
		yield 'misc_flag', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_tiles', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'misc_flag_2', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'dxgi_format', name_type_map['DxgiFormat'], (0, None), (False, None)
		yield 'resource_dimension', name_type_map['D3D10ResourceDimension'], (0, None), (False, None)
		yield 'misc_flag', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_tiles', name_type_map['Uint'], (0, None), (False, 1)
		yield 'misc_flag_2', name_type_map['Uint'], (0, None), (False, None)
