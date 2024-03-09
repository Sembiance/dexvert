from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class OvsHeader(BaseStruct):

	"""
	Description of one archive's content
	"""

	__name__ = 'OvsHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.pool_groups = Array(self.context, 0, None, (0,), name_type_map['PoolGroup'])
		self.pools = Array(self.context, 0, None, (0,), name_type_map['MemPool'])
		self.data_entries = Array(self.context, 0, None, (0,), name_type_map['DataEntry'])
		self.buffer_entries = Array(self.context, 0, None, (0,), name_type_map['BufferEntry'])
		self.buffer_groups = Array(self.context, 0, None, (0,), name_type_map['BufferGroup'])
		self.root_entries = Array(self.context, 0, None, (0,), name_type_map['RootEntry'])
		self.fragments = Array(self.context, 0, None, (0,), name_type_map['Fragment'])
		self.set_header = name_type_map['SetHeader'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pool_groups', Array, (0, None, (None,), name_type_map['PoolGroup']), (False, None), (None, None)
		yield 'pools', Array, (0, None, (None,), name_type_map['MemPool']), (False, None), (None, None)
		yield 'data_entries', Array, (0, None, (None,), name_type_map['DataEntry']), (False, None), (None, None)
		yield 'buffer_entries', Array, (0, None, (None,), name_type_map['BufferEntry']), (False, None), (None, None)
		yield 'buffer_groups', Array, (0, None, (None,), name_type_map['BufferGroup']), (False, None), (None, None)
		yield 'root_entries', Array, (0, None, (None,), name_type_map['RootEntry']), (False, None), (None, None)
		yield 'fragments', Array, (0, None, (None,), name_type_map['Fragment']), (False, None), (None, None)
		yield 'set_header', name_type_map['SetHeader'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pool_groups', Array, (0, None, (instance.arg.num_pool_groups,), name_type_map['PoolGroup']), (False, None)
		yield 'pools', Array, (0, None, (instance.arg.num_pools,), name_type_map['MemPool']), (False, None)
		yield 'data_entries', Array, (0, None, (instance.arg.num_datas,), name_type_map['DataEntry']), (False, None)
		yield 'buffer_entries', Array, (0, None, (instance.arg.num_buffers,), name_type_map['BufferEntry']), (False, None)
		yield 'buffer_groups', Array, (0, None, (instance.arg.num_buffer_groups,), name_type_map['BufferGroup']), (False, None)
		yield 'root_entries', Array, (0, None, (instance.arg.num_root_entries,), name_type_map['RootEntry']), (False, None)
		yield 'fragments', Array, (0, None, (instance.arg.num_fragments,), name_type_map['Fragment']), (False, None)
		yield 'set_header', name_type_map['SetHeader'], (0, None), (False, None)
