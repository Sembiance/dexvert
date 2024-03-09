from nifgen.array import Array
from nifgen.formats.ovl.imports import name_type_map
from nifgen.formats.ovl_base.compounds.GenericHeader import GenericHeader


class Header(GenericHeader):

	"""
	Found at the beginning of every OVL file
	"""

	__name__ = 'Header'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# counts ovs files with unique paths not matching the ovl name; all LODs of one type count as 1
		self.num_ovs_types = name_type_map['Uint'](self.context, 0, None)

		# length of the Names block below, including 00 bytes
		self.len_names = name_type_map['Uint'](self.context, 0, None)
		self.zero_2 = name_type_map['Uint'](self.context, 0, None)

		# count of external aux files, ie audio banks
		self.num_aux_entries = name_type_map['Uint'](self.context, 0, None)

		# count of included ovl files that are available to this ovl
		self.num_included_ovls = name_type_map['Ushort'](self.context, 0, None)

		# count of file mime types, aka. extensions with metadata
		self.num_mimes = name_type_map['Ushort'](self.context, 0, None)
		self.num_files = name_type_map['Uint'](self.context, 0, None)

		# repeat count of files ??
		self.num_files_2 = name_type_map['Uint'](self.context, 0, None)
		self.num_dependencies = name_type_map['Uint'](self.context, 0, None)

		# number of archives
		self.num_archives = name_type_map['Uint'](self.context, 0, None)

		# across all archives
		self.num_pool_groups = name_type_map['Uint'](self.context, 0, None)

		# across all archives
		self.num_pools = name_type_map['Uint'](self.context, 0, None)

		# across all archives
		self.num_datas = name_type_map['Uint'](self.context, 0, None)

		# across all archives
		self.num_buffers = name_type_map['Uint'](self.context, 0, None)

		# number of files in external OVS archives
		self.num_stream_files = name_type_map['Uint'](self.context, 0, None)

		# used in ZTUAC elephants
		self.ztuac_unk_0 = name_type_map['Uint'](self.context, 0, None)

		# used in ZTUAC elephants
		self.ztuac_unk_1 = name_type_map['Uint'](self.context, 0, None)

		# used in ZTUAC elephants
		self.ztuac_unk_2 = name_type_map['Uint'](self.context, 0, None)

		# length of archive names
		self.len_archive_names = name_type_map['Uint'](self.context, 0, None)

		# another Num Files
		self.num_files_3 = name_type_map['Uint'](self.context, 0, None)

		# length of the type names portion inside Names block (usually at the start), not counting 00 bytes
		self.len_type_names = name_type_map['Uint'](self.context, 0, None)

		# used in PZ1.6 for the first time
		self.num_triplets = name_type_map['Uint'](self.context, 0, None)

		# zeros
		self.reserved = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# Name buffer for assets and file mime types.
		self.names = name_type_map['ZStringBuffer'](self.context, self.len_names, None)

		# used in DLA
		self.names_pad = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.mimes = Array(self.context, 0, None, (0,), name_type_map['MimeEntry'])
		self.triplets_ref = name_type_map['Empty'](self.context, 0, None)
		self.triplets = Array(self.context, 0, None, (0,), name_type_map['Triplet'])
		self.triplets_pad = name_type_map['PadAlign'](self.context, 4, self.triplets_ref)
		self.files = Array(self.context, 0, None, (0,), name_type_map['FileEntry'])

		# usually STATIC followed by any external OVS names
		self.archive_names = name_type_map['ZStringBuffer'](self.context, self.len_archive_names, None)
		self.archives = Array(self.context, 0, None, (0,), name_type_map['ArchiveEntry'])
		self.included_ovls = Array(self.context, 0, None, (0,), name_type_map['IncludedOvl'])
		self.dependencies = Array(self.context, 0, None, (0,), name_type_map['DependencyEntry'])
		self.aux_entries = Array(self.context, 0, None, (0,), name_type_map['AuxEntry'])

		# after aux in ZTUAC and PC
		self.dependencies = Array(self.context, 0, None, (0,), name_type_map['DependencyEntry'])
		self.stream_files = Array(self.context, 0, None, (0,), name_type_map['StreamEntry'])
		self.archives_meta = Array(self.context, 0, None, (0,), name_type_map['ArchiveMeta'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_ovs_types', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'len_names', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_aux_entries', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_included_ovls', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_mimes', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_files', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_files_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_dependencies', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_archives', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_pool_groups', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_pools', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_datas', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_buffers', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_stream_files', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ztuac_unk_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ztuac_unk_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ztuac_unk_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'len_archive_names', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_files_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'len_type_names', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_triplets', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'reserved', Array, (0, None, (12,), name_type_map['Uint']), (False, None), (None, None)
		yield 'names', name_type_map['ZStringBuffer'], (None, None), (False, None), (None, None)
		yield 'names_pad', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (lambda context: context.version <= 15, None)
		yield 'mimes', Array, (0, None, (None,), name_type_map['MimeEntry']), (False, None), (None, None)
		yield 'triplets_ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'triplets', Array, (0, None, (None,), name_type_map['Triplet']), (False, None), (lambda context: context.version >= 20, None)
		yield 'triplets_pad', name_type_map['PadAlign'], (4, None), (False, None), (lambda context: context.version >= 20, None)
		yield 'files', Array, (0, None, (None,), name_type_map['FileEntry']), (False, None), (None, None)
		yield 'archive_names', name_type_map['ZStringBuffer'], (None, None), (False, None), (None, None)
		yield 'archives', Array, (0, None, (None,), name_type_map['ArchiveEntry']), (False, None), (None, None)
		yield 'included_ovls', Array, (0, None, (None,), name_type_map['IncludedOvl']), (False, None), (None, None)
		yield 'dependencies', Array, (0, None, (None,), name_type_map['DependencyEntry']), (False, None), (lambda context: context.version >= 19, None)
		yield 'aux_entries', Array, (0, None, (None,), name_type_map['AuxEntry']), (False, None), (None, None)
		yield 'dependencies', Array, (0, None, (None,), name_type_map['DependencyEntry']), (False, None), (lambda context: context.version <= 18, None)
		yield 'stream_files', Array, (0, None, (None,), name_type_map['StreamEntry']), (False, None), (None, None)
		yield 'archives_meta', Array, (0, None, (None,), name_type_map['ArchiveMeta']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_ovs_types', name_type_map['Uint'], (0, None), (False, None)
		yield 'len_names', name_type_map['Uint'], (0, None), (False, None)
		yield 'zero_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_aux_entries', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_included_ovls', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_mimes', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_files', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_files_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_dependencies', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_archives', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_pool_groups', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_pools', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_datas', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_buffers', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_stream_files', name_type_map['Uint'], (0, None), (False, None)
		yield 'ztuac_unk_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'ztuac_unk_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'ztuac_unk_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'len_archive_names', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_files_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'len_type_names', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_triplets', name_type_map['Uint'], (0, None), (False, None)
		yield 'reserved', Array, (0, None, (12,), name_type_map['Uint']), (False, None)
		yield 'names', name_type_map['ZStringBuffer'], (instance.len_names, None), (False, None)
		if instance.context.version <= 15:
			yield 'names_pad', Array, (0, None, ((16 - (instance.len_names % 16)) % 16,), name_type_map['Ubyte']), (False, None)
		yield 'mimes', Array, (0, None, (instance.num_mimes,), name_type_map['MimeEntry']), (False, None)
		yield 'triplets_ref', name_type_map['Empty'], (0, None), (False, None)
		if instance.context.version >= 20:
			yield 'triplets', Array, (0, None, (instance.num_triplets,), name_type_map['Triplet']), (False, None)
			yield 'triplets_pad', name_type_map['PadAlign'], (4, instance.triplets_ref), (False, None)
		yield 'files', Array, (0, None, (instance.num_files,), name_type_map['FileEntry']), (False, None)
		yield 'archive_names', name_type_map['ZStringBuffer'], (instance.len_archive_names, None), (False, None)
		yield 'archives', Array, (0, None, (instance.num_archives,), name_type_map['ArchiveEntry']), (False, None)
		yield 'included_ovls', Array, (0, None, (instance.num_included_ovls,), name_type_map['IncludedOvl']), (False, None)
		if instance.context.version >= 19:
			yield 'dependencies', Array, (0, None, (instance.num_dependencies,), name_type_map['DependencyEntry']), (False, None)
		yield 'aux_entries', Array, (0, None, (instance.num_aux_entries,), name_type_map['AuxEntry']), (False, None)
		if instance.context.version <= 18:
			yield 'dependencies', Array, (0, None, (instance.num_dependencies,), name_type_map['DependencyEntry']), (False, None)
		yield 'stream_files', Array, (0, None, (instance.num_stream_files,), name_type_map['StreamEntry']), (False, None)
		yield 'archives_meta', Array, (0, None, (instance.num_archives,), name_type_map['ArchiveMeta']), (False, None)
