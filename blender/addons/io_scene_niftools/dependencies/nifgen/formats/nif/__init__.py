from nifgen.formats.nif.imports import name_type_map
from importlib import import_module
from io import BytesIO
from itertools import chain
import logging
import os
import re

from nifgen.formats.nif.imports import name_type_map
from nifgen.array import Array
from nifgen.formats.nif.basic import Uint, FileVersion, Ulittle32, LineString, HeaderString, switchable_endianness, Ref, Ptr, NiFixedString, basic_map
from nifgen.formats.nif.bsmain.structs.BSStreamHeader import BSStreamHeader
from nifgen.formats.nif.enums.DataStreamUsage import DataStreamUsage
from nifgen.formats.nif.enums.EndianType import EndianType
from nifgen.formats.nif.bitflagss.DataStreamAccess import DataStreamAccess
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject
from nifgen.formats.nif.nimain.structs.Header import Header
from nifgen.formats.nif.nimain.structs.Footer import Footer
from nifgen.formats.nif.nimain.structs.SizedString import SizedString
from nifgen.formats.nif.nimain.structs.FilePath import FilePath
from nifgen.formats.nif.nimain.structs.String import String
from nifgen.formats.nif.versions import has_bs_ver, available_versions


class _attr_dict(dict):

	def __getattr__(self, key):
		return self[key]


def create_niclasses_map():
	"""Goes through the entire directory of the nif format to find all defined
	classes and put them in a map of {local_name: class}"""
	niclasses_map = _attr_dict()
	for name, class_object in name_type_map.items():
		niclasses_map[name] = class_object
	return niclasses_map


def safe_decode(b: bytes, encodings=('ascii', 'utf8', 'latin1', 'shift-jis')) -> str:
	for encoding in encodings:
		try:
			return b.decode(encoding)
		except UnicodeDecodeError:
			pass
	return b.decode("ascii", errors="surrogateescape")


def encode(s: str, encoding='utf-8') -> bytes:
	# since utf-8 contains all characters of the other encodings, encoding to it is a safe guess
	return s.encode("utf-8", errors="surrogateescape")


def class_post_processor(defined_class, processed_classes):
	# create the _has_links, _has_refs and _has_strings class variables
	# set all three to None just in case of infinite recursion
	if defined_class in processed_classes:
		return defined_class
	defined_class._has_links = None
	defined_class._has_refs = None
	defined_class._has_strings = None
	processed_classes.add(defined_class)
	if getattr(defined_class, "_attribute_list", None) is not None:
		attribute_list = defined_class._attribute_list
		fields_links = [None] * len(attribute_list)
		fields_refs = [None] * len(attribute_list)
		fields_strings = [None] * len(attribute_list)
		for i, (f_name, f_type, args, *_) in enumerate(attribute_list):
			if isinstance(f_type, type) and issubclass(f_type, Array):
				f_type = args[3]
			if f_type is None:
				# type is unknown, so you always have to check
				fields_links[i] = True
				fields_refs[i] = True
				fields_strings[i] = True
				continue
			if not f_type in processed_classes:
				class_post_processor(f_type, processed_classes)
			fields_links[i] = f_type._has_links
			fields_refs[i] = f_type._has_refs
			fields_strings[i] = f_type._has_strings
		defined_class._has_links = any(fields_links)
		defined_class._has_refs = any(fields_refs)
		defined_class._has_strings = any(fields_strings)
	else:
		# is a basic, enum, bitfield or basic-like, therefore has no reference
		# technically bitfields could contain links, but no existing one does at the moment
		defined_class._has_links = issubclass(defined_class, (Ptr, Ref))
		defined_class._has_refs = issubclass(defined_class, Ref)
		defined_class._has_strings = issubclass(defined_class, (String, FilePath, NiFixedString))
	return defined_class


def djb1_hash(type_name):
	hash_val = 0
	for x in type_name:
		hash_val = ((33 * hash_val) + ord(x)) & 0xFFFFFFFF
	return hash_val


# filter for recognizing NIF files by extension
# .kf are NIF files containing keyframes
# .kfa are NIF files containing keyframes in DAoC style
# .nifcache are Empire Earth II NIF files
# .texcache are Empire Earth II/III packed texture NIF files
# .pcpatch are Empire Earth II/III packed texture NIF files
# .item are Divinity 2 NIF files
# .nft are Bully SE NIF files (containing textures)
# .nif_wii are Epic Mickey NIF files
file_extensions = ["nif", "kf", "kfa", "jmi", "texcache", "pcpatch", "nif_wii"]
file_extensions += list(set(chain.from_iterable([version.ext for version in available_versions])))
RE_FILENAME = re.compile(fr"^.*\.({'|'.join(file_extensions)})$", re.IGNORECASE)
# archives
ARCHIVE_CLASSES = [] # link to the actual bsa format once done
# used for comparing floats
EPSILON = 0.0001

classes = create_niclasses_map()
classes.update(basic_map)
processed_classes = set()
for defined_class in classes.values():
	class_post_processor(defined_class, processed_classes)
niobject_map = {niclass.__name__: niclass for niclass in classes.values() if issubclass(niclass, NiObject)}
hash_name_map = {djb1_hash(name): name for name in niobject_map.keys()}


# exceptions
class NifError(Exception):
	"""Standard nif exception class."""
	pass


class NifFile(Header):
	"""A class to contain the actual nif data.

	Note that {blocks} are not automatically kept
	in sync with the rest of the nif data, but they are
	resynchronized when calling L{write}.

	:ivar version: The nif version.
	:type version: int
	:ivar user_version: The nif user version.
	:type user_version: int
	:ivar roots: List of root blocks.
	:type roots: list[NiObject]
	:ivar blocks: List of blocks.
	:type blocks: list[NiObject]
	:ivar modification: Neo Steam ("neosteam") or Ndoors ("ndoors") or Joymaster Interactive Howling Sword ("jmihs1") or Laxe Lore ("laxelore") style nif?
	:type modification: str
	"""

	def __init__(self, context=None, arg=0, template=None, set_default=True):
		# user version and bs version will be set by init
		# use self as context
		super().__init__(self, arg, template, set_default=set_default)
		self.roots = []
		self.blocks = []
		self.modification = None

	@staticmethod
	def inspect_version_only(stream):
		pos = stream.tell()
		try:
			header_string = HeaderString.from_stream(stream)
			h_ver, modification = HeaderString.version_modification_from_headerstring(header_string)
			if h_ver <= 0x03010000:
				LineString.from_stream(stream)
				LineString.from_stream(stream)
				LineString.from_stream(stream)
			if h_ver < 0x03010001:
				ver_int = h_ver
			else:
				ver_int = FileVersion.from_stream(stream)
			# special case for Laxe Lore
			if h_ver == 0x14000004 and ver_int == 0x5A000004:
				modification = "laxelore"
			# neosteam and ndoors have a special version integer
			elif (not modification) or modification == "jmihs1":
				 if ver_int != h_ver:
					 raise ValueError(f"Corrupted NIF file: header version string in {header_string} does not "
					   f"correspond with header version field {ver_int}")
			elif modification == "neosteam":
				if ver_int != 0x08F35232:
					raise ValueError("Corrupted NIF file: invalid NeoSteam version.")
			elif modification == "ndoors":
				if ver_int != 0x73615F67:
					raise ValueError("Corrupted NIF file: invalid Ndoors version.")
			# read EndianType to advance stream
			if ver_int >= 0x14000004:
				EndianType.from_stream(stream)
			user = 0
			bsver = 0
			if ver_int >= 0x0A010000:
				user = Ulittle32.from_stream(stream)
				# only need to set bsver if Bethesda
				if has_bs_ver(ver_int, user):
					# read num_blocks
					Ulittle32.from_stream(stream)
					bsver = Ulittle32.from_stream(stream)
			return modification, (ver_int, user, bsver)
		finally:
			stream.seek(pos)

	@classmethod
	def from_version(cls, version=0x04000002, user_version=0, user_version_2=0):
		"""Initialize nif data. By default, this creates an empty
		nif document of the given version and user version.

		:param version: The version.
		:type version: int
		:param user_version: The user version.
		:type user_version: int
		"""
		instance = cls()
		instance.version = version
		instance.user_version = user_version
		for f_name, f_type, arguments, (optional, default) in cls._get_filtered_attribute_list(instance):
			if f_name == "version":
				continue
			elif f_name == "user_version":
				continue
			elif f_name == "bs_header":
				field_value = BSStreamHeader.from_bs_version(instance, user_version_2)
			else:
				if default is None:
					field_value = f_type(instance, *arguments)
				else:
					field_value = f_type.from_value(*arguments[2:4], default)
			setattr(instance, f_name, field_value)
		cls.update_globals(instance)
		return instance

	def read_blocks(self, stream):
		logger = logging.getLogger("generated.formats.nif")
		self.roots = []
		self.blocks = []
		self._block_dct = {}

		block_num = 0
		while True:
			if self.version < 0x0303000D:
				pos = stream.tell()
				top_level_str = SizedString.from_stream(stream, self)
				if top_level_str == "Top Level Object":
					# check if this is a 'Top Level Object'
					is_root = True
				else:
					is_root = False
					stream.seek(pos)
			else:
				if block_num >= self.num_blocks:
					break
				# signal as no root for now, roots are added when the footer
				# is read
				is_root = False

			# get block name
			if self.version >= 0x05000001:
				# note the 0xfff mask: required for the NiPhysX blocks
				type_index = self.block_type_index[block_num] & 0xfff
				if self.version == 0x14030102:
					# Fantasy Frontier and Aura Kingdom only have the NiObject type map through a hash value
					block_type = hash_name_map[self.block_type_hashes[type_index]]
				else:
					block_type = self.block_types[type_index]
				# handle data stream classes:
				if block_type.startswith("NiDataStream\x01"):
					block_type, data_stream_usage, data_stream_access = block_type.split("\x01")
					data_stream_usage = int(data_stream_usage)
					data_stream_access = int(data_stream_access)
				# read dummy integer
				# bhk blocks are *not* preceeded by a dummy
				if self.version <= 0x0A01006A and not block_type.startswith("bhk"):
					dummy = Uint.from_stream(stream)
					if dummy != 0:
						raise NifError(f'non-zero block tag {dummy} at {stream.tell()})')
			else:
				block_type = SizedString.from_stream(stream, self)
			# get the block index
			if self.version >= 0x0303000D:
				# for these versions the block index is simply the block number
				block_index = block_num
			else:
				# earlier versions
				# the number of blocks is not in the header
				# and a special block type string marks the end of the file
				if block_type == "End Of File": break
					# read the block index, which is probably the memory
					# location of the object when it was written to
					# memory
				else:
					block_index = Uint.from_stream(stream)
					if block_index in self._block_dct:
						raise NifError(f'duplicate block index ({block_index} at {stream.tell()})')
			# create the block
			try:
				block_class = niobject_map[block_type]
			except KeyError:
				error_msg = f"Unknown block type {block_type} on stream position {stream.tell()} with index {len(self.blocks)}."
				if self.version > 0x14020007:
					error_msg = error_msg + f" Block length is {self.block_size[block_num]}"
				raise ValueError(error_msg)
			logger.debug(f"Reading {block_type} block at {stream.tell()}")
			# read the block
			try:
				block = block_class.from_stream(stream, self, 0, None)
			except:
				logger.exception(f"Reading {block_class} failed")
				raise
			# complete NiDataStream data
			if block_type == "NiDataStream":
				block.usage = DataStreamUsage.from_value(data_stream_usage)
				block.access = DataStreamAccess.from_value(data_stream_access)
			self._block_dct[block_index] = block
			self.blocks.append(block)
			# check block size
			if self.version > 0x14020007:
				logger.debug("Checking block size")
				calculated_size = block.io_size
				if calculated_size != self.block_size[block_num]:
					extra_size = self.block_size[block_num] - calculated_size
					logger.error("Block size check failed: corrupt NIF file or bad nif.xml?")
					logger.error(f"Skipping {extra_size} bytes in block [{block_index}]{block_type} at position {block.io_start} to {stream.tell()}")
					# skip bytes that were missed
					stream.seek(extra_size, 1)
			# add block to roots if flagged as such
			if is_root:
				self.roots.append(block)
			# check if we are done
			block_num += 1

	def read_footer(self, stream):
		logger = logging.getLogger("generated.formats.nif")
		ftr = Footer.from_stream(stream, self)
		# check if we are at the end of the file
		if stream.read(1):
			logger.error('End of file not reached: corrupt NIF file?')

		# add root objects in footer to roots list
		if self.version >= 0x0303000D:
			for root in ftr.roots:
				if root >= 0:
					self.roots.append(self.blocks[root])

	# GlobalNode
	def get_global_child_nodes(self, edge_filter=()):
		return (root for root in self.roots)

	@staticmethod
	def update_globals(instance):
		"""Update information after setting version and/or endianness."""
		[basic.update_struct(instance) for basic in switchable_endianness]
		if instance.version == 0x14020007 and instance.user_version == 12 and instance.bs_header.bs_version >= 83:
			# Skyrim and later
			instance.havok_scale = 1 / 0.0142875
		else:
			# any other time
			instance.havok_scale = 1 / 0.142875

	@staticmethod
	def get_string_classes(version):
		if version >= 0x14010003:
			return (String, FilePath, NiFixedString)
		else:
			return (NiFixedString,)

	def get_strings(self, instance):
		"""Get all strings in the structure."""
		str_classes = self.get_string_classes(self.version)

		def field_has_strings(attr_def):
			if issubclass(attr_def[1], Array):
				f_type = attr_def[2][3]
			else:
				f_type = attr_def[1]
			return f_type._has_strings

		condition_function = lambda x: issubclass(x[1], str_classes)
		for val in self.get_condition_values_recursive(instance, condition_function, enter_condition=field_has_strings):
			if val:
				yield val

	def get_recursive_strings(self, instance):
		"""Get all strings in the entire tree"""

		# The condition where the header has a string list is similar, but not the same as where String and FilePath have a
		# NiFixedString. Therefore, it is theoretically possible to have a header with a string list where Strings and
		# FilePaths do not reference that. However, it is not possible with the currently know valid nif versions.
		str_classes = self.get_string_classes(self.version)

		def field_has_strings(attr_def):
			if issubclass(attr_def[1], Array):
				f_type = attr_def[2][3]
			else:
				f_type = attr_def[1]
			return f_type._has_refs or f_type._has_strings

		condition_function = lambda x: issubclass(x[1], (*str_classes, Ref))

		parsed_blocks = set()

		def _get_recursive_strings_block(block):
			for s_type, s_inst, (f_name, f_type, arguments, _) in self.get_condition_attributes_recursive(type(block), block, condition_function, enter_condition=field_has_strings):
				value = s_type.get_field(s_inst, f_name)
				if issubclass(f_type, Ref):
					if value is not None and value not in parsed_blocks:
						yield from _get_recursive_strings_block(value)
				else:
					# must be a string type
					if value:
						yield value
			parsed_blocks.add(block)

		yield from _get_recursive_strings_block(instance)

	def resolve_references(self):
		# go through every NiObject and replace references and pointers with the
		# actual object they're pointing to
		def field_has_links(attr_def):
			if issubclass(attr_def[1], Array):
				f_type = attr_def[2][3]
			else:
				f_type = attr_def[1]
			return f_type._has_links
		is_ref = lambda attribute: issubclass(attribute[1], (Ref, Ptr))
		for block in self.blocks:
			for parent_type, parent_instance, attribute in self.get_condition_attributes_recursive(type(block), block, is_ref, enter_condition=field_has_links):
				block_index = parent_type.get_field(parent_instance, attribute[0])
				if isinstance(block_index, int):
					if self.version >= 0x0303000D:
						if block_index == -1:
							resolved_ref = None
						else:
							try:
								resolved_ref = self.blocks[block_index]
							except IndexError:
								raise IndexError(f"block index {block_index} exceeds limit {len(self.blocks)} of block list."
						               f"Field '{attribute[0]}' of {parent_type} in block {self.blocks.index(block)}")
					else:
						if block_index == 0:
							resolved_ref = None
						else:
							try:
								resolved_ref = self._block_dct[block_index]
							except KeyError:
								raise IndexError(f"block index {block_index} not found in block map {list(self._block_dct.keys())}."
						               f"Field '{attribute[0]}' of {parent_type} in block {self.blocks.index(block)}")

					parent_type.set_field(parent_instance, attribute[0], resolved_ref)

	def _makeBlockList(self, root, block_index_dct, block_type_list, block_type_dct):
		"""This is a helper function for write to set up the list of all blocks,
		the block index map, and the block type map.

		:param root: The root block, whose tree is to be added to
			the block list.
		:type root: L{NifFormat.NiObject}
		:param block_index_dct: Dictionary mapping blocks in self.blocks to
			their block index.
		:type block_index_dct: dict
		:param block_type_list: List of all block types.
		:type block_type_list: list of str
		:param block_type_dct: Dictionary mapping blocks in self.blocks to
			their block type index.
		:type block_type_dct: dict
		"""
		def _blockChildBeforeParent(block):
			"""Determine whether block comes before its parent or not, depending
			on the block type.

			@todo: Move to the L{NifFormat.Data} class.

			:param block: The block to test.
			:type block: L{NifFormat.NiObject}
			:return: ``True`` if child should come first, ``False`` otherwise.
			"""
			return (isinstance(block, niobject_map["bhkRefObject"])
					and not isinstance(block, niobject_map["bhkConstraint"]))

		# block already listed? if so, return
		if root in self.blocks:
			return

		# add block type to block type dictionary
		block_type = type(root).__name__
		# special case: NiDataStream stores part of data in block type list
		if block_type == "NiDataStream":
			block_type = f"NiDataStream\x01{int(root.usage)}\x01{int(root.access)}"
		try:
			block_type_dct[root] = block_type_list.index(block_type)
		except ValueError:
			block_type_dct[root] = len(block_type_list)
			block_type_list.append(block_type)

		# special case: add bhkConstraint entities before bhkConstraint
		# (these are actually links, not refs)
		if isinstance(root, niobject_map["bhkConstraint"]):
			for entity in root.entities:
				if entity is not None:
					self._makeBlockList(entity, block_index_dct, block_type_list, block_type_dct)

		children_left = []
		# add children that come before the block
		# store any remaining children in children_left (processed later)
		for child in root.get_refs():
			if _blockChildBeforeParent(child):
				self._makeBlockList(child, block_index_dct, block_type_list, block_type_dct)
			else:
				children_left.append(child)

		# add the block
		if self.version >= 0x030300D:
			block_index_dct[root] = len(self.blocks)
		else:
			block_index_dct[root] = id(root)
		self.blocks.append(root)

		for child in children_left:
			self._makeBlockList(child, block_index_dct, block_type_list, block_type_dct)

	@classmethod
	def read_fields(cls, stream, instance):
		for field_name, field_type, arguments, (optional, default) in cls._get_filtered_attribute_list(instance, include_abstract=False):
			field_value = field_type.from_stream(stream, instance.context, *arguments)
			setattr(instance, field_name, field_value)
			if field_name == "header_string":
				ver, modification = HeaderString.version_modification_from_headerstring(field_value)
				instance.version = ver
				instance.modification = modification
				cls.update_globals(instance)
			if field_name in {"version", "endian_type", "user_version", "bs_header"}:
				# update every basic and other important constants - these fields are used in determining how basics
				# are read and other important settings
				cls.update_globals(instance)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)

	def write(self, stream):
		return type(self).to_stream(self, stream, self)

	@classmethod
	def from_stream(cls, stream, context=None, arg=0, template=None):
		instance = cls(context, arg, template, set_default=False)
		instance.io_start = stream.tell()
		logger = logging.getLogger("generated.formats.nif")
		logger.debug(f"Reading header at {stream.tell()}")
		cls.read_fields(stream, instance)
		logger.debug(f"Version {instance.version}")
		instance.io_size = stream.tell() - instance.io_start
		# read the separete NiObjects to build the block list
		instance.read_blocks(stream)
		# resolve references (Refs and Pointers) using the block list
		instance.resolve_references()
		# read the Footer
		instance.read_footer(stream)
		return instance

	@classmethod
	def to_stream(cls, instance, stream, context=None, argument=0, template=None):
		logger = logging.getLogger("generated.formats.nif")
		# the context (i.e. the file) is stored on the stream
		stream.context = instance
		# set up index and type dictionary
		instance.blocks = [] # list of all blocks to be written
		instance._block_index_dct = {} # maps block to block index
		block_type_list = [] # list of all block type strings
		block_type_dct = {} # maps block to block type string index
		instance._string_list = []
		# create/update the block list before anything else
		for root in instance.roots:
			instance._makeBlockList(root, instance._block_index_dct, block_type_list, block_type_dct)
			if instance.version >= 0x14010001:
				instance._string_list.extend(instance.get_recursive_strings(root))
# 			recursive strings (at least for test maplestory 2 (30.2.0.3) nif) is more true to base game order
# 			than get_strings per block
# 			for block in cls.tree(root):
# 				instance._string_list.extend(cls.get_strings(block))
		instance._string_list = list({string: None for string in instance._string_list})  # ensure unique elements

		instance.num_blocks = len(instance.blocks)
		instance.num_block_types = len(block_type_list)
		instance.reset_field("block_types")
		instance.block_types[:] = block_type_list
		instance.reset_field("block_type_index")
		instance.block_type_index[:] = [block_type_dct[block] for block in instance.blocks]
		if instance.version >= 0x14010001:
			instance.num_strings = len(instance._string_list)
			if instance._string_list:
				instance.max_string_length = max([SizedString.get_size(s, instance) - 4 for s in instance._string_list])
			else:
				instance.max_string_length = 0
			instance.reset_field("strings")
			instance.strings[:] = instance._string_list
		if instance.version >= 0x14020005:
			instance.reset_field("block_size")
			instance.block_size[:] = [type(block).get_size(block, instance, 0, None) for block in instance.blocks]

		# update the basics before doing any writing
		cls.update_globals(instance)
		# write the header (instance)
		logger.debug("Writing header")
		instance.io_start = stream.tell()
		cls.write_fields(stream, instance)
		instance.io_size = stream.tell() - instance.io_start

		# write the blocks
		for block in instance.blocks:
			# signal top level object if block is a root object
			if instance.version < 0x0303000D and block in instance.roots:
				SizedString.to_stream("Top Level Object", stream, instance)
			if instance.version >= 0x05000001:
				if instance.version <= 0x0A01006A:
					# write zero dummy separator
					Uint.to_stream(0, stream, instance)
			else:
				# write block type string
				assert(block_type_list[block_type_dct[block]] == type(block).__name__)
				SizedString.to_stream(type(block).__name__, stream, instance)
			# write block index
			logger.debug(f"Writing {type(block).__name__} block")
			if instance.version < 0x0303000D:
				Uint.to_stream(instance._block_index_dct[block], stream, instance) # original pyffi code had Int
			# write block
			type(block).to_stream(block, stream, instance)
		if instance.version < 0x0303000D:
			SizedString.to_stream("End Of File", stream, instance)

		# write the Footer
		ftr = Footer(instance)
		ftr.num_roots = len(instance.roots)
		ftr.roots[:] = instance.roots
		Footer.to_stream(ftr, stream, instance)
		return instance

	def validate(self):
		type(self).validate_instance(self, self, 0, None)
		for root in self.roots:
			for block in root.tree(unique=True):
				type(block).validate_instance(block, self, arg=0, template=None)

	@classmethod
	def from_path(cls, filepath):
		with open(filepath, "rb") as stream:
			return cls.from_stream(stream)

	@classmethod
	def to_path(cls, filepath, instance):
		with open(filepath, "wb") as stream:
			cls.to_stream(instance, stream, instance)

__xml_version__ = "0.10.0.0"

if __name__ == "__main__":
	pass