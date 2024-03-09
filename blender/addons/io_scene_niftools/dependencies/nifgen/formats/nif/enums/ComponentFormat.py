import numpy as np

from nifgen.base_struct import BaseStruct
from nifgen.bitfield import BasicBitfield, BitfieldMember
import nifgen.formats.nif.basic as NifBasic
import nifgen.formats.base.basic as BaseBasic


class NormByte(NifBasic.NormClass):

	storage = BaseBasic.Byte

	@staticmethod
	def from_function(instance):
        # function based on Epic Mickey AL_Interior_BlackBox01.nif_wii
        # best guess - however, is not necessarily the only correct function
		return (2 * instance + 1) / 255

	@staticmethod
	def to_function(instance):
		return np.round(((255 * instance) - 1) / 2)


class UNormByte(NifBasic.UNormClass):

	storage = NifBasic.Byte

	@staticmethod
	def from_function(instance):
		return instance / 255.0

	@staticmethod
	def to_function(instance):
		return np.round(instance * 255)


class NormShort(NifBasic.NormClass):

	storage = NifBasic.Short

	@staticmethod
	def from_function(instance):
		return (2 * instance + 1) / 65535

	@staticmethod
	def to_function(instance):
		return np.round(((65535 * instance) - 1) / 2)


class UNormShort(NifBasic.UNormClass):

	storage = NifBasic.Ushort

	@staticmethod
	def from_function(instance):
		return instance / 65535.0

	@staticmethod
	def to_function(instance):
		return np.round(instance * 65535.0)


class NormInt(NifBasic.NormClass):

	storage = NifBasic.Int

	@staticmethod
	def from_function(instance):
		return (2 * instance + 1) / 4294967295

	@staticmethod
	def to_function(instance):
		return np.round(((4294967295 * instance) - 1) / 2)


class UNormInt(NifBasic.UNormClass):

	storage = NifBasic.Uint

	@staticmethod
	def from_function(instance):
		return instance / 4294967295.0

	@staticmethod
	def to_function(instance):
		return np.round(instance * 4294967295.0)


class Format40(NifBasic.UNormClass):
	"""Seems to be shorts divided by 1023, based on EM UV map"""

	storage = NifBasic.Short

	@staticmethod
	def from_value(value):
		return min(max(0.0, value), 64.06158357771261)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert instance >= 0.0
		assert instance <= 64.06158357771261

	@staticmethod
	def from_function(instance):
		return instance / 1023.0

	@staticmethod
	def to_function(instance):
		return np.round(instance * 1023.0)


class Bitfield39(BasicBitfield):
	c1 = BitfieldMember(pos=0, mask=0x3FF, return_type=int)
	c2 = BitfieldMember(pos=10, mask=0xFFC00, return_type=int)
	c3 = BitfieldMember(pos=20, mask=0x3FF00000, return_type=int)
from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class ComponentFormat(BaseEnum):

	"""
	The data format of components. Mask 0x00FF0000 to get the number of subfields. Mask 0x0000FF00 to get the size of each subfield.
	It's not a bitfield, because the values are not independent.
	"""

	__name__ = 'ComponentFormat'
	_storage = Uint


	# Unknown, or don't care, format.
	F_UNKNOWN = 0x00000000
	F_INT8_1 = 0x00010101
	F_INT8_2 = 0x00020102
	F_INT8_3 = 0x00030103
	F_INT8_4 = 0x00040104
	F_UINT8_1 = 0x00010105
	F_UINT8_2 = 0x00020106
	F_UINT8_3 = 0x00030107
	F_UINT8_4 = 0x00040108
	F_NORMINT8_1 = 0x00010109
	F_NORMINT8_2 = 0x0002010A
	F_NORMINT8_3 = 0x0003010B
	F_NORMINT8_4 = 0x0004010C
	F_NORMUINT8_1 = 0x0001010D
	F_NORMUINT8_2 = 0x0002010E
	F_NORMUINT8_3 = 0x0003010F
	F_NORMUINT8_4 = 0x00040110
	F_INT16_1 = 0x00010211
	F_INT16_2 = 0x00020212
	F_INT16_3 = 0x00030213
	F_INT16_4 = 0x00040214
	F_UINT16_1 = 0x00010215
	F_UINT16_2 = 0x00020216
	F_UINT16_3 = 0x00030217
	F_UINT16_4 = 0x00040218
	F_NORMINT16_1 = 0x00010219
	F_NORMINT16_2 = 0x0002021A
	F_NORMINT16_3 = 0x0003021B
	F_NORMINT16_4 = 0x0004021C
	F_NORMUINT16_1 = 0x0001021D
	F_NORMUINT16_2 = 0x0002021E
	F_NORMUINT16_3 = 0x0003021F
	F_NORMUINT16_4 = 0x00040220
	F_INT32_1 = 0x00010421
	F_INT32_2 = 0x00020422
	F_INT32_3 = 0x00030423
	F_INT32_4 = 0x00040424
	F_UINT32_1 = 0x00010425
	F_UINT32_2 = 0x00020426
	F_UINT32_3 = 0x00030427
	F_UINT32_4 = 0x00040428
	F_NORMINT32_1 = 0x00010429
	F_NORMINT32_2 = 0x0002042A
	F_NORMINT32_3 = 0x0003042B
	F_NORMINT32_4 = 0x0004042C
	F_NORMUINT32_1 = 0x0001042D
	F_NORMUINT32_2 = 0x0002042E
	F_NORMUINT32_3 = 0x0003042F
	F_NORMUINT32_4 = 0x00040430
	F_FLOAT16_1 = 0x00010231
	F_FLOAT16_2 = 0x00020232
	F_FLOAT16_3 = 0x00030233
	F_FLOAT16_4 = 0x00040234
	F_FLOAT32_1 = 0x00010435
	F_FLOAT32_2 = 0x00020436
	F_FLOAT32_3 = 0x00030437
	F_FLOAT32_4 = 0x00040438
	F_UINT_10_10_10_L1 = 0x00010439
	F_NORMINT_10_10_10_L1 = 0x0001043A
	F_NORMINT_11_11_10 = 0x0001043B
	F_NORMUINT8_4_BGRA = 0x0004013C
	F_NORMINT_10_10_10_2 = 0x0001043D
	F_UINT_10_10_10_2 = 0x0001043E
	F_UNKNOWN_20240 = 0x00020240

	_non_members_ = ["_storage", "struct_map"]

	struct_map = {}

	@classmethod
	def struct_for_type(cls, format_type):
		# note: does not agree with noesis
		if format_type == cls.F_UNKNOWN.type_id:
			# raw bytes
			return NifBasic.Byte
		elif cls.F_INT8_1.type_id <= format_type <= cls.F_INT8_4.type_id:
			# signed byte
			return BaseBasic.Byte
		elif cls.F_UINT8_1.type_id <= format_type <= cls.F_UINT8_4.type_id:
			# unsigned byte
			return NifBasic.Byte
		elif cls.F_NORMINT8_1.type_id <= format_type <= cls.F_NORMINT8_4.type_id:
			# normalized signed byte
			return NormByte
		elif cls.F_NORMUINT8_1.type_id <= format_type <= cls.F_NORMUINT8_4.type_id:
			# normalized unsigned byte
			return UNormByte
		elif cls.F_INT16_1.type_id <= format_type <= cls.F_INT16_4.type_id:
			# signed short
			return NifBasic.Short
		elif cls.F_UINT16_1.type_id <= format_type <= cls.F_UINT16_4.type_id:
			# unsigned short
			return NifBasic.Ushort
		elif cls.F_NORMINT16_1.type_id <= format_type <= cls.F_NORMINT16_4.type_id:
			# normalized signed short
			return NormShort
		elif cls.F_NORMUINT16_1.type_id <= format_type <= cls.F_NORMUINT16_4.type_id:
			# normalized unsigned short
			return UNormShort
		elif cls.F_INT32_1.type_id <= format_type <= cls.F_INT32_4.type_id:
			# signed int32
			return NifBasic.Int
		elif cls.F_UINT32_1.type_id <= format_type <= cls.F_UINT32_4.type_id:
			# unsigned int32
			return NifBasic.Uint
		elif cls.F_NORMINT32_1.type_id <= format_type <= cls.F_NORMINT32_4.type_id:
			# normalized signed int32
			return NormInt
		elif cls.F_NORMUINT32_1.type_id <= format_type <= cls.F_NORMUINT32_4.type_id:
			# normalized unsigned int32
			return UNormInt
		elif cls.F_FLOAT16_1.type_id <= format_type <= cls.F_FLOAT16_4.type_id:
			# hfloat
			return NifBasic.Hfloat
		elif cls.F_FLOAT32_1.type_id <= format_type <= cls.F_FLOAT32_4.type_id:
			# float32
			return NifBasic.Float
		elif format_type == cls.F_UINT_10_10_10_L1.type_id:
			return Bitfield39
		elif format_type == cls.F_NORMINT_10_10_10_L1.type_id:
			# return simple int for now
			return NifBasic.Int
		elif format_type == cls.F_NORMINT_11_11_10.type_id:
			# return simple int for now
			return NifBasic.Int
		elif format_type == cls.F_NORMUINT8_4_BGRA.type_id:
			# like color4 but switched around - individual components are unormbyte
			return UNormByte
		elif format_type == cls.F_NORMINT_10_10_10_2.type_id:
			# return simple int for now
			return NifBasic.Int
		elif format_type == cls.F_UINT_10_10_10_2.type_id:
			# return simple int for now
			return NifBasic.Int
		elif format_type == cls.F_UNKNOWN_20240.type_id:
			# non-standard format guess based on Epic Mickey UV map.
			return Format40
		raise NotImplementedError

	@property
	def type_id(self):
		return self & 0xFF

	@property
	def element_width(self):
		return (self & 0x0000FF00) >> 8

	@property
	def num_elements(self):
		return (self & 0x00FF0000) >> 16

	@classmethod
	def get_component_size(cls, format_description):
		return format_description.element_width * format_description.num_elements

	@classmethod
	def create_struct_from_format(cls, format_description):
		# create a struct representing the componentformat description
		element_type = cls.struct_for_type(format_description & 0xFF)
		if format_description.num_elements <= 1:
			return element_type
		else:
			field_names = [f"c{i}" for i in range(format_description.num_elements)]


			class created_struct(BaseStruct):

				__name__  = format_description.name

				@staticmethod
				def _get_attribute_list():
					for f_name in field_names:
						yield (f_name, element_type, (0, None), (False, None), (None, None))

				@staticmethod
				def _get_filtered_attribute_list(instance, include_abstract=True):
					for f_name in field_names:
						yield f_name, element_type, (0, None), (False, None)

			created_struct.init_attributes()

			return created_struct

	@classmethod
	def struct_for_format(cls, format_description):
		if format_description in cls.struct_map:
			return cls.struct_map[format_description]
		else:
			created_struct = cls.create_struct_from_format(format_description)
			cls.struct_map[format_description] = created_struct
			return created_struct
