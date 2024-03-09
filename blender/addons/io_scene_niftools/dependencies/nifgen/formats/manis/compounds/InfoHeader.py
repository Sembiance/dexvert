from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class InfoHeader(BaseStruct):

	"""
	Custom header struct
	"""

	__name__ = 'InfoHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.version = name_type_map['Uint'](self.context, 0, None)
		self.mani_count = name_type_map['Uint'](self.context, 0, None)
		self.names = Array(self.context, 0, None, (0,), name_type_map['ZString'])
		self.header = name_type_map['ManisRoot'](self.context, 0, None)
		self.mani_infos = Array(self.context, 0, None, (0,), name_type_map['ManiInfo'])
		self.name_buffer = name_type_map['Buffer1'](self.context, int(self.header.hash_block_size / 4), None)
		self.keys_buffer = name_type_map['KeysReader'](self.context, self.mani_infos, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'version', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'mani_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'names', Array, (0, None, (None,), name_type_map['ZString']), (False, None), (None, None)
		yield 'header', name_type_map['ManisRoot'], (0, None), (False, None), (None, None)
		yield 'mani_infos', Array, (0, None, (None,), name_type_map['ManiInfo']), (False, None), (None, None)
		yield 'name_buffer', name_type_map['Buffer1'], (None, None), (False, None), (None, None)
		yield 'keys_buffer', name_type_map['KeysReader'], (None, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'version', name_type_map['Uint'], (0, None), (False, None)
		yield 'mani_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'names', Array, (0, None, (instance.mani_count,), name_type_map['ZString']), (False, None)
		yield 'header', name_type_map['ManisRoot'], (0, None), (False, None)
		yield 'mani_infos', Array, (0, None, (instance.mani_count,), name_type_map['ManiInfo']), (False, None)
		yield 'name_buffer', name_type_map['Buffer1'], (int(instance.header.hash_block_size / 4), None), (False, None)
		yield 'keys_buffer', name_type_map['KeysReader'], (instance.mani_infos, None), (False, None)
