import logging

from nifgen.base_struct import BaseStruct
from nifgen.formats.base.compounds.PadAlign import get_padding
from modules.formats.shared import get_padding_size

from nifgen.base_struct import BaseStruct


class SegmentsReader(BaseStruct):

	__name__ = 'SegmentsReader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	@classmethod
	def read_fields(cls, stream, instance):
		instance.io_start = stream.tell()
		# print(instance.context)
		for segment in instance.arg:
			segment.data = stream.read(segment.byte_size)
			pad_size = get_padding_size(segment.byte_size)
			segment.padding = stream.read(pad_size)
			assert segment.padding == b"\x00" * pad_size
		logging.debug(f"Compressed keys data ends at {stream.tell()}")
		instance.io_size = stream.tell() - instance.io_start

	@classmethod
	def write_fields(cls, stream, instance):
		instance.io_start = stream.tell()
		for segment in instance.arg:
			stream.write(segment.data)
			stream.write(get_padding(segment.byte_size))
		instance.io_size = stream.tell() - instance.io_start

	@classmethod
	def get_fields_str(cls, instance, indent=0):
		s = ''
		for mani_info in instance.arg:
			if hasattr(mani_info, "keys"):
				s += str(mani_info.keys)
		return s


