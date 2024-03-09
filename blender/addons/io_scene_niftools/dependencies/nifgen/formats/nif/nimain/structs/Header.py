from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Header(BaseStruct):

	"""
	The NIF file header.
	"""

	__name__ = 'Header'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 'NetImmerse File Format x.x.x.x' (versions <= 10.0.1.2) or 'Gamebryo File Format x.x.x.x' (versions >= 10.1.0.0), with x.x.x.x the version written out. Ends with a newline character (0x0A).
		self.header_string = name_type_map['HeaderString'](self.context, 0, None)
		self.copyright = Array(self.context, 0, None, (0,), name_type_map['LineString'])

		# The NIF version, in hexadecimal notation: 0x04000002, 0x0401000C, 0x04020002, 0x04020100, 0x04020200, 0x0A000100, 0x0A010000, 0x0A020000, 0x14000004, ...
		self.version = name_type_map['FileVersion'].from_value(67108866)

		# Determines the endianness of the data in the file.
		self.endian_type = name_type_map['EndianType'].ENDIAN_LITTLE

		# An extra version number, for companies that decide to modify the file format.
		self.user_version = name_type_map['Ulittle32'](self.context, 0, None)

		# Number of file objects.
		self.num_blocks = name_type_map['Ulittle32'](self.context, 0, None)
		self.bs_header = name_type_map['BSStreamHeader'](self.context, 0, None)
		self.metadata = name_type_map['ByteArray'](self.context, 0, None)

		# Number of object types in this NIF file.
		self.num_block_types = name_type_map['Ushort'](self.context, 0, None)

		# List of all object types used in this NIF file.
		self.block_types = Array(self.context, 0, None, (0,), name_type_map['SizedString'])

		# List of all object types used in this NIF file.
		self.block_type_hashes = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# Maps file objects on their corresponding type: first file object is of type object_types[object_type_index[0]], the second of object_types[object_type_index[1]], etc.
		self.block_type_index = Array(self.context, 0, None, (0,), name_type_map['BlockTypeIndex'])

		# Array of block sizes
		self.block_size = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# Number of strings.
		self.num_strings = name_type_map['Uint'](self.context, 0, None)

		# Maximum string length.
		self.max_string_length = name_type_map['Uint'](self.context, 0, None)

		# Strings.
		self.strings = Array(self.context, 0, None, (0,), name_type_map['SizedString'])
		self.num_groups = name_type_map['Uint'].from_value(0)
		self.groups = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'header_string', name_type_map['HeaderString'], (0, None), (False, None), (None, None)
		yield 'copyright', Array, (0, None, (3,), name_type_map['LineString']), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'version', name_type_map['FileVersion'], (0, None), (False, 67108866), (lambda context: context.version >= 50397185, None)
		yield 'endian_type', name_type_map['EndianType'], (0, None), (False, name_type_map['EndianType'].ENDIAN_LITTLE), (lambda context: context.version >= 335544323, None)
		yield 'user_version', name_type_map['Ulittle32'], (0, None), (False, None), (lambda context: context.version >= 167772424, None)
		yield 'num_blocks', name_type_map['Ulittle32'], (0, None), (False, None), (lambda context: context.version >= 50397185, None)
		yield 'bs_header', name_type_map['BSStreamHeader'], (0, None), (False, None), (None, True)
		yield 'metadata', name_type_map['ByteArray'], (0, None), (False, None), (lambda context: context.version >= 503316480, None)
		yield 'num_block_types', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 83886081, None)
		yield 'block_types', Array, (0, None, (None,), name_type_map['SizedString']), (False, None), (lambda context: context.version >= 83886081, True)
		yield 'block_type_hashes', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: 335741186 <= context.version <= 335741186, None)
		yield 'block_type_index', Array, (0, None, (None,), name_type_map['BlockTypeIndex']), (False, None), (lambda context: context.version >= 83886081, None)
		yield 'block_size', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: context.version >= 335675397, None)
		yield 'num_strings', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335609857, None)
		yield 'max_string_length', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335609857, None)
		yield 'strings', Array, (0, None, (None,), name_type_map['SizedString']), (False, None), (lambda context: context.version >= 335609857, None)
		yield 'num_groups', name_type_map['Uint'], (0, None), (False, 0), (lambda context: context.version >= 83886086, None)
		yield 'groups', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: context.version >= 83886086, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'header_string', name_type_map['HeaderString'], (0, None), (False, None)
		if instance.context.version <= 50397184:
			yield 'copyright', Array, (0, None, (3,), name_type_map['LineString']), (False, None)
		if instance.context.version >= 50397185:
			yield 'version', name_type_map['FileVersion'], (0, None), (False, 67108866)
		if instance.context.version >= 335544323:
			yield 'endian_type', name_type_map['EndianType'], (0, None), (False, name_type_map['EndianType'].ENDIAN_LITTLE)
		if instance.context.version >= 167772424:
			yield 'user_version', name_type_map['Ulittle32'], (0, None), (False, None)
		if instance.context.version >= 50397185:
			yield 'num_blocks', name_type_map['Ulittle32'], (0, None), (False, None)
		if (instance.version == 167772418) or (((instance.version == 335675399) or ((instance.version == 335544325) or ((instance.version >= 167837696) and ((instance.version <= 335544324) and (instance.user_version <= 11))))) and (instance.user_version >= 3)):
			yield 'bs_header', name_type_map['BSStreamHeader'], (0, None), (False, None)
		if instance.context.version >= 503316480:
			yield 'metadata', name_type_map['ByteArray'], (0, None), (False, None)
		if instance.context.version >= 83886081:
			yield 'num_block_types', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 83886081 and instance.version != 335741186:
			yield 'block_types', Array, (0, None, (instance.num_block_types,), name_type_map['SizedString']), (False, None)
		if 335741186 <= instance.context.version <= 335741186:
			yield 'block_type_hashes', Array, (0, None, (instance.num_block_types,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 83886081:
			yield 'block_type_index', Array, (0, None, (instance.num_blocks,), name_type_map['BlockTypeIndex']), (False, None)
		if instance.context.version >= 335675397:
			yield 'block_size', Array, (0, None, (instance.num_blocks,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 335609857:
			yield 'num_strings', name_type_map['Uint'], (0, None), (False, None)
			yield 'max_string_length', name_type_map['Uint'], (0, None), (False, None)
			yield 'strings', Array, (0, None, (instance.num_strings,), name_type_map['SizedString']), (False, None)
		if instance.context.version >= 83886086:
			yield 'num_groups', name_type_map['Uint'], (0, None), (False, 0)
			yield 'groups', Array, (0, None, (instance.num_groups,), name_type_map['Uint']), (False, None)
