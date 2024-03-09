from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class ArchiveEntry(BaseStruct):

	"""
	Description of one archive
	"""

	__name__ = 'ArchiveEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['OffsetString'](self.context, self.context.archive_names, None)

		# starting index in ovl list of pools, this archive's pools continue for num_pools
		self.pools_offset = name_type_map['Uint'](self.context, 0, None)

		# starting index into ovl.stream_files
		self.stream_files_offset = name_type_map['Uint'](self.context, 0, None)

		# Total amount of pools in this archive; sum of all PoolGroup.num_pools
		self.num_pools = name_type_map['Uint'](self.context, 0, None)

		# Amount of Data Entries
		self.num_datas = name_type_map['Ushort'](self.context, 0, None)

		# Amount of PoolGroup objects at start of this deflated archive.
		self.num_pool_groups = name_type_map['Ushort'](self.context, 0, None)
		self.num_buffer_groups = name_type_map['Uint'](self.context, 0, None)

		# Amount of buffers in the archive
		self.num_buffers = name_type_map['Uint'](self.context, 0, None)

		# Amount of Fragments in the archive
		self.num_fragments = name_type_map['Uint'](self.context, 0, None)

		# Number of files in the archive
		self.num_root_entries = name_type_map['Uint'](self.context, 0, None)

		# Seek to pos to get zlib header for this archive
		self.read_start = name_type_map['Uint'](self.context, 0, None)

		# size of the set and asset entry data
		self.set_data_size = name_type_map['Uint'](self.context, 0, None)

		# size of the compressed data for this archive
		self.compressed_size = name_type_map['Uint'](self.context, 0, None)

		# size of the uncompressed data for this archive
		self.uncompressed_size = name_type_map['Uint64'](self.context, 0, None)

		# byte offset, cumulative size of all pools preceding this archive
		self.pools_start = name_type_map['Uint'](self.context, 0, None)

		# byte offset, pools_start + sum of this archive's pools' sizes
		self.pools_end = name_type_map['Uint'](self.context, 0, None)

		# Seemingly unused, can be zeroed without effect ingame in JWE
		self.ovs_offset = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'pools_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'stream_files_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_pools', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_datas', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_pool_groups', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_buffer_groups', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_buffers', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_fragments', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_root_entries', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'read_start', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'set_data_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'compressed_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'uncompressed_size', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'pools_start', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'pools_end', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ovs_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['OffsetString'], (instance.context.archive_names, None), (False, None)
		yield 'pools_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'stream_files_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_pools', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_datas', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_pool_groups', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_buffer_groups', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_buffers', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_fragments', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_root_entries', name_type_map['Uint'], (0, None), (False, None)
		yield 'read_start', name_type_map['Uint'], (0, None), (False, None)
		yield 'set_data_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'compressed_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'uncompressed_size', name_type_map['Uint64'], (0, None), (False, None)
		yield 'pools_start', name_type_map['Uint'], (0, None), (False, None)
		yield 'pools_end', name_type_map['Uint'], (0, None), (False, None)
		yield 'ovs_offset', name_type_map['Uint'], (0, None), (False, None)
