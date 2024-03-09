from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class UnkChunkList(BaseStruct):

	__name__ = 'UnkChunkList'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ref = name_type_map['Empty'](self.context, 0, None)
		self.zero_0 = name_type_map['SmartPadding'](self.context, 0, None)
		self.subchunk_count = name_type_map['Ushort'](self.context, 0, None)
		self.flag = name_type_map['Ushort'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint'](self.context, 0, None)
		self.chunksize_list = Array(self.context, 0, None, (0,), name_type_map['ChunkSizes'])
		self.subchunk_list = name_type_map['SubChunkReader'](self.context, self.chunksize_list, None)

		# ?
		self.pad = name_type_map['PadAlign'](self.context, 16, self.ref)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'zero_0', name_type_map['SmartPadding'], (0, None), (False, None), (None, None)
		yield 'subchunk_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'flag', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'chunksize_list', Array, (0, None, (None,), name_type_map['ChunkSizes']), (False, None), (None, None)
		yield 'subchunk_list', name_type_map['SubChunkReader'], (None, None), (False, None), (None, None)
		yield 'pad', name_type_map['PadAlign'], (16, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ref', name_type_map['Empty'], (0, None), (False, None)
		yield 'zero_0', name_type_map['SmartPadding'], (0, None), (False, None)
		yield 'subchunk_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'flag', name_type_map['Ushort'], (0, None), (False, None)
		yield 'zero_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'chunksize_list', Array, (0, None, (instance.subchunk_count,), name_type_map['ChunkSizes']), (False, None)
		yield 'subchunk_list', name_type_map['SubChunkReader'], (instance.chunksize_list, None), (False, None)
		yield 'pad', name_type_map['PadAlign'], (16, instance.ref), (False, None)
