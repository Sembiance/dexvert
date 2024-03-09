from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.tex.imports import name_type_map


class TexHeader(MemStruct):

	"""
	DLA: 24 bytes, no pointers
	ZTUAC, PC: 24 bytes, with 1 pointer
	JWE, PZ, JWE2: 40 bytes, with 2 pointers
	"""

	__name__ = 'TexHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zero_0 = name_type_map['Uint64'].from_value(0)
		self.zero_1 = name_type_map['Uint64'].from_value(0)
		self.compression_type = name_type_map['DdsType'](self.context, 0, None)

		# 0 or 1
		self.one_0 = name_type_map['Ubyte'](self.context, 0, None)
		self.num_mips = name_type_map['Ushort'](self.context, 0, None)
		self.width = name_type_map['Ushort'](self.context, 0, None)
		self.height = name_type_map['Ushort'](self.context, 0, None)

		# amount of files combined in this texture, usually 1 or 2, 3 for JWE2 rex
		self.stream_count = name_type_map['Ubyte'](self.context, 0, None)

		# usually as above
		self.stream_count_repeat = name_type_map['Ubyte'](self.context, 0, None)

		# 0; 1 for PC
		self.pad = name_type_map['Uint'].from_value(0)
		self.pad_dla = name_type_map['Uint64'].from_value(0)
		self.buffer_infos = name_type_map['ArrayPointer'](self.context, self.stream_count, name_type_map['TexBuffer'])
		self.size_info = name_type_map['Pointer'](self.context, 0, name_type_map['SizeInfo'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zero_0', name_type_map['Uint'], (0, None), (True, 0), (lambda context: context.version <= 15, None)
		yield 'zero_0', name_type_map['Uint64'], (0, None), (True, 0), (lambda context: context.version >= 17, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (True, 0), (lambda context: context.version >= 19, None)
		yield 'buffer_infos', name_type_map['ArrayPointer'], (None, name_type_map['TexBufferPc']), (False, None), (lambda context: 17 <= context.version <= 18, None)
		yield 'buffer_infos', name_type_map['ArrayPointer'], (None, name_type_map['TexBuffer']), (False, None), (lambda context: context.version >= 19, None)
		yield 'size_info', name_type_map['Pointer'], (0, name_type_map['SizeInfo']), (False, None), (lambda context: context.version >= 19, None)
		yield 'compression_type', name_type_map['DdsTypeCoaster'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'compression_type', name_type_map['DdsType'], (0, None), (False, None), (lambda context: context.version >= 19, None)
		yield 'one_0', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'num_mips', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 15, None)
		yield 'width', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 15, None)
		yield 'height', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 15, None)
		yield 'stream_count', name_type_map['Ubyte'], (0, None), (False, None), (lambda context: context.version >= 17, None)
		yield 'stream_count_repeat', name_type_map['Ubyte'], (0, None), (False, None), (lambda context: context.version >= 17, None)
		yield 'pad', name_type_map['Uint'], (0, None), (True, 0), (None, None)
		yield 'pad_dla', name_type_map['Uint64'], (0, None), (True, 0), (lambda context: context.version <= 15, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 15:
			yield 'zero_0', name_type_map['Uint'], (0, None), (True, 0)
		if instance.context.version >= 17:
			yield 'zero_0', name_type_map['Uint64'], (0, None), (True, 0)
		if instance.context.version >= 19:
			yield 'zero_1', name_type_map['Uint64'], (0, None), (True, 0)
		if 17 <= instance.context.version <= 18:
			yield 'buffer_infos', name_type_map['ArrayPointer'], (instance.stream_count, name_type_map['TexBufferPc']), (False, None)
		if instance.context.version >= 19:
			yield 'buffer_infos', name_type_map['ArrayPointer'], (instance.stream_count, name_type_map['TexBuffer']), (False, None)
			yield 'size_info', name_type_map['Pointer'], (0, name_type_map['SizeInfo']), (False, None)
		if instance.context.version <= 18:
			yield 'compression_type', name_type_map['DdsTypeCoaster'], (0, None), (False, None)
		if instance.context.version >= 19:
			yield 'compression_type', name_type_map['DdsType'], (0, None), (False, None)
		yield 'one_0', name_type_map['Ubyte'], (0, None), (False, None)
		if instance.context.version <= 15:
			yield 'num_mips', name_type_map['Ushort'], (0, None), (False, None)
			yield 'width', name_type_map['Ushort'], (0, None), (False, None)
			yield 'height', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 17:
			yield 'stream_count', name_type_map['Ubyte'], (0, None), (False, None)
			yield 'stream_count_repeat', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'pad', name_type_map['Uint'], (0, None), (True, 0)
		if instance.context.version <= 15:
			yield 'pad_dla', name_type_map['Uint64'], (0, None), (True, 0)
