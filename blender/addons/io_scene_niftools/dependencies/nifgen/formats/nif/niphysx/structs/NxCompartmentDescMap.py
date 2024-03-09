from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NxCompartmentDescMap(BaseStruct):

	__name__ = 'NxCompartmentDescMap'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.id = name_type_map['Uint'](self.context, 0, None)
		self.type = name_type_map['NxCompartmentType'].SCT_RIGIDBODY
		self.device_code = name_type_map['NxDeviceCode'].CPU
		self.grid_hash_cell_size = name_type_map['Float'].from_value(100.0)
		self.grid_hash_table_power = name_type_map['Uint'].from_value(8)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'id', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'type', name_type_map['NxCompartmentType'], (0, None), (False, name_type_map['NxCompartmentType'].SCT_RIGIDBODY), (None, None)
		yield 'device_code', name_type_map['NxDeviceCode'], (0, None), (False, name_type_map['NxDeviceCode'].CPU), (None, None)
		yield 'grid_hash_cell_size', name_type_map['Float'], (0, None), (False, 100.0), (None, None)
		yield 'grid_hash_table_power', name_type_map['Uint'], (0, None), (False, 8), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'id', name_type_map['Uint'], (0, None), (False, None)
		yield 'type', name_type_map['NxCompartmentType'], (0, None), (False, name_type_map['NxCompartmentType'].SCT_RIGIDBODY)
		yield 'device_code', name_type_map['NxDeviceCode'], (0, None), (False, name_type_map['NxDeviceCode'].CPU)
		yield 'grid_hash_cell_size', name_type_map['Float'], (0, None), (False, 100.0)
		yield 'grid_hash_table_power', name_type_map['Uint'], (0, None), (False, 8)
