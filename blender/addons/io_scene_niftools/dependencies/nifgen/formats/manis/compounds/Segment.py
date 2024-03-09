from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class Segment(BaseStruct):

	__name__ = 'Segment'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# seen 0 or 2
		self.unk_a = name_type_map['Uint'](self.context, 0, None)

		# seen 0 or 2
		self.unk_b = name_type_map['Uint'](self.context, 0, None)
		self.ptr_ori_result = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_pos_result = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_scale_0_result = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_scale_1_result = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_morph_result = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_compressed_mani_data = name_type_map['Uint64'](self.context, 0, None)

		# to be read sequentially starting after this array
		self.byte_size = name_type_map['Uint64'](self.context, 0, None)
		self.ptr_compressed_keys = name_type_map['Uint64'](self.context, 0, None)
		self.zeros_1 = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk_a', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_b', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ptr_ori_result', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_pos_result', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_scale_0_result', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_scale_1_result', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_morph_result', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_compressed_mani_data', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'byte_size', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ptr_compressed_keys', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zeros_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk_a', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_b', name_type_map['Uint'], (0, None), (False, None)
		yield 'ptr_ori_result', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_pos_result', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_scale_0_result', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_scale_1_result', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_morph_result', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_compressed_mani_data', name_type_map['Uint64'], (0, None), (False, None)
		yield 'byte_size', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ptr_compressed_keys', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zeros_1', name_type_map['Uint64'], (0, None), (False, None)
