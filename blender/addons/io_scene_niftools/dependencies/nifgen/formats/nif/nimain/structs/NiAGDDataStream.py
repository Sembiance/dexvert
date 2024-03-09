from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiAGDDataStream(BaseStruct):

	__name__ = 'NiAGDDataStream'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Type of data in this channel
		self.type = name_type_map['Uint'](self.context, 0, None)

		# Number of bytes per element of this channel
		self.unit_size = name_type_map['Uint'](self.context, 0, None)

		# Total number of bytes of this channel (num vertices times num bytes per element)
		self.total_size = name_type_map['Uint'](self.context, 0, None)

		# Number of bytes per element in all channels together. Sum of num channel bytes per element over all block infos.
		self.stride = name_type_map['Uint'](self.context, 0, None)

		# Unsure. The block in which this channel is stored? Usually there is only one block, and so this is zero.
		self.block_index = name_type_map['Uint'](self.context, 0, None)

		# Offset (in bytes) of this channel. Sum of all num channel bytes per element of all preceeding block infos.
		self.block_offset = name_type_map['Uint'](self.context, 0, None)
		self.flags = name_type_map['NiAGDDataStreamFlags'].from_value(2)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'type', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unit_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'total_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'stride', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'block_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'block_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'flags', name_type_map['NiAGDDataStreamFlags'], (0, None), (False, 2), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'type', name_type_map['Uint'], (0, None), (False, None)
		yield 'unit_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'total_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'stride', name_type_map['Uint'], (0, None), (False, None)
		yield 'block_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'block_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'flags', name_type_map['NiAGDDataStreamFlags'], (0, None), (False, 2)
