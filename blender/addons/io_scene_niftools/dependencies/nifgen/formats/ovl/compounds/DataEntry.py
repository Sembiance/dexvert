
import logging

from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class DataEntry(BaseStruct):

	"""
	32 bytes
	"""

	__name__ = 'DataEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# djb2 hash
		self.file_hash = name_type_map['Uint'](self.context, 0, None)

		# djb2 hash for extension
		self.ext_hash = name_type_map['Uint'](self.context, 0, None)

		# 1-based indexing into set_header.sets; 0 if data is not part of a set
		self.set_index = name_type_map['Ushort'](self.context, 0, None)

		# number of buffers that should be read from list for this entry
		self.buffer_count = name_type_map['Ushort'](self.context, 0, None)
		self.zero = name_type_map['Uint'](self.context, 0, None)

		# size of first buffer, in the case of the ms2 the size 1 is the size of the first two buffers together
		self.size_1 = name_type_map['Uint64'](self.context, 0, None)

		# size of last buffer; tex and texstream have all size here
		self.size_2 = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ext_hash', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 19, None)
		yield 'set_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'buffer_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 19, None)
		yield 'size_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'size_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 19:
			yield 'ext_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'set_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'buffer_count', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 19:
			yield 'zero', name_type_map['Uint'], (0, None), (False, None)
		yield 'size_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'size_2', name_type_map['Uint64'], (0, None), (False, None)

	def update_data(self, datas):
		"""Load datas into this DataEntry's buffers, and update its size values according to an assumed pattern
		data : list of bytes object, each representing the data of one buffer for this data entry"""
		for buffer, data in zip(self.sorted_buffers, datas):
			buffer.update_data(data)
		# update data 0, 1 size
		# total = sum(len(d) for d in datas)
		if len(datas) == 1:
			self.size_1 = len(datas[0])
			self.size_2 = 0
		elif len(datas) == 2:
			self.size_1 = 0
			self.size_2 = sum(len(d) for d in datas)
		elif len(datas) > 2:
			self.size_1 = sum(len(d) for d in datas[:2])
			self.size_2 = sum(len(d) for d in datas[2:])

	@property
	def sorted_buffers(self):
		"""Get buffers sorted by index"""
		return sorted(self.buffers, key=lambda buffer: buffer.index)

	@property
	def buffer_datas(self):
		"""Get data for each buffer"""
		return list(buffer.data for buffer in self.sorted_buffers)

	def __eq__(self, other):
		attr_check = ("buffer_count", "size_1", "size_2")
		same = True
		for attr in attr_check:
			a = getattr(self, attr)
			b = getattr(other, attr)
			if a != b:
				logging.warning(f"Data differs for '{attr}' - {a} vs {b}")
				same = False
		for i, (a, b) in enumerate(zip(self.sorted_buffers, other.sorted_buffers)):
			if a != b:
				logging.warning(f"Buffer {i} differs for {a} vs {b}")
				same = False
		return same

