from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class BufferGroup(BaseStruct):

	"""
	32 bytes
	"""

	__name__ = 'BufferGroup'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# first buffer index
		self.buffer_offset = name_type_map['Uint'](self.context, 0, None)

		# number of buffers to grab
		self.buffer_count = name_type_map['Uint'](self.context, 0, None)

		# type of extension this entry is for
		self.ext_index = name_type_map['Uint'](self.context, 0, None)

		# which buffer index to populate
		self.buffer_index = name_type_map['Uint'](self.context, 0, None)

		# cumulative size of all buffers to grab
		self.size = name_type_map['Uint64'](self.context, 0, None)

		# first data entry
		self.data_offset = name_type_map['Uint'](self.context, 0, None)

		# number of data entries to populate buffers into
		self.data_count = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'buffer_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'buffer_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ext_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'buffer_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'size', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data_count', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'buffer_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'buffer_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'ext_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'buffer_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'size', name_type_map['Uint64'], (0, None), (False, None)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'data_count', name_type_map['Uint'], (0, None), (False, None)
