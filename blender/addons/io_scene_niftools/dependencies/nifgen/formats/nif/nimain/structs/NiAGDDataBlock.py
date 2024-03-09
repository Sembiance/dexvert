from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiAGDDataBlock(BaseStruct):

	__name__ = 'NiAGDDataBlock'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.block_size = name_type_map['Uint'](self.context, 0, None)
		self.num_blocks = name_type_map['Uint'](self.context, 0, None)
		self.block_offsets = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.num_data = name_type_map['Uint'](self.context, 0, None)
		self.data_sizes = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.data = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.shader_index = name_type_map['Uint'](self.context, 0, None)
		self.total_size = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'block_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_blocks', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'block_offsets', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'num_data', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data_sizes', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'data', Array, (0, None, (None, None,), name_type_map['Byte']), (False, None), (None, None)
		yield 'shader_index', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'total_size', name_type_map['Uint'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'block_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_blocks', name_type_map['Uint'], (0, None), (False, None)
		yield 'block_offsets', Array, (0, None, (instance.num_blocks,), name_type_map['Uint']), (False, None)
		yield 'num_data', name_type_map['Uint'], (0, None), (False, None)
		yield 'data_sizes', Array, (0, None, (instance.num_data,), name_type_map['Uint']), (False, None)
		yield 'data', Array, (0, None, (instance.num_data, instance.block_size,), name_type_map['Byte']), (False, None)
		if instance.arg == 1:
			yield 'shader_index', name_type_map['Uint'], (0, None), (False, None)
			yield 'total_size', name_type_map['Uint'], (0, None), (False, None)
