import logging

from nifgen.base_struct import BaseStruct
from nifgen.formats.base.basic import Ushort, Ubyte
from nifgen.formats.manis.compounds.ManiBlock import ManiBlock

from nifgen.base_struct import BaseStruct


class KeysReader(BaseStruct):

	__name__ = 'KeysReader'


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
		for mani_info in instance.arg:
			# logging.info(mani_info)
			mani_block_start = stream.tell()
			logging.debug(f"Reading keys block at {mani_block_start}")
			# if mani_block_start == 964833:
			# 	break
			bone_dtype = Ushort if mani_info.dtype.use_ushort else Ubyte
			try:
				mani_info.keys = ManiBlock.from_stream(stream, instance.context, mani_info, bone_dtype)
				# logging.info(mani_info)
				# logging.info(mani_info.keys)
				# break
			except:
				logging.exception(f"Reading ManiBlock failed at {mani_block_start} for {mani_info}")
		instance.io_size = stream.tell() - instance.io_start

	@classmethod
	def write_fields(cls, stream, instance):
		instance.io_start = stream.tell()
		for mani_info in instance.arg:
			ManiBlock.to_stream(mani_info.keys, stream, instance.context)
		instance.io_size = stream.tell() - instance.io_start

	@classmethod
	def get_fields_str(cls, instance, indent=0):
		s = ''
		for mani_info in instance.arg:
			if hasattr(mani_info, "keys"):
				s += str(mani_info.keys)
		return s


