from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl_base.imports import name_type_map


class GenericHeader(BaseStruct):

	"""
	Found at the beginning of every OVL file
	"""

	__name__ = 'GenericHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 'FRES' for ovl
		self.magic = name_type_map['FixedString'](self.context, 4, None)

		# if 0x08 then 64bit, 0x01 for JWE, PZ, 0x08 for PC, 0x48 for JWE Switch, may be platform
		self.version_flag = name_type_map['Byte'](self.context, 0, None)

		# 0x12 = PC, 0x13 = JWE, PZ
		self.version = name_type_map['Byte'](self.context, 0, None)

		# endianness?, usually zero
		self.bitswap = name_type_map['Byte'](self.context, 0, None)

		# always = 1
		self.seventh_byte = name_type_map['Byte'].from_value(1)

		# determines compression format (none, zlib or oodle) and apparently type of data (additional fields)
		self.user_version = name_type_map['VersionInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'magic', name_type_map['FixedString'], (4, None), (False, None), (None, None)
		yield 'version_flag', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'version', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'bitswap', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'seventh_byte', name_type_map['Byte'], (0, None), (False, 1), (None, None)
		yield 'user_version', name_type_map['VersionInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'magic', name_type_map['FixedString'], (4, None), (False, None)
		yield 'version_flag', name_type_map['Byte'], (0, None), (False, None)
		yield 'version', name_type_map['Byte'], (0, None), (False, None)
		yield 'bitswap', name_type_map['Byte'], (0, None), (False, None)
		yield 'seventh_byte', name_type_map['Byte'], (0, None), (False, 1)
		yield 'user_version', name_type_map['VersionInfo'], (0, None), (False, None)
