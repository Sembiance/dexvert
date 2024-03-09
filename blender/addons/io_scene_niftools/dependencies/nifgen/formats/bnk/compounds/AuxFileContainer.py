import logging
import os

from nifgen.formats.bnk.compounds.BKHDSection import BKHDSection
from nifgen.formats.bnk.compounds.DATASection import DATASection
from nifgen.formats.bnk.compounds.DIDXSection import DIDXSection
from nifgen.formats.bnk.compounds.HIRCSection import HIRCSection
from nifgen.base_struct import BaseStruct
from nifgen.formats.base.compounds.PadAlign import get_padding
from modules.formats.shared import fmt_hash


class AuxFileContainer(BaseStruct):
	# Custom file struct

	def __init__(self, context, arg=0, template=None, set_default=False):
		super().__init__(context, arg, template, set_default=False)
		self.chunks = []
		self.bhkd = None
		self.didx = None
		self.hirc = None
		self.data = None
		self.size_for_ovl = 0
		self.old_size = 0

	@classmethod
	def read_fields(cls, stream, instance):
		instance.chunks = []
		chunk_id = "DUMM"
		while len(chunk_id) == 4:
			chunk_id = stream.read(4)
			after_size_pos = stream.tell() + 4
			logging.debug(f"reading chunk {chunk_id} at {stream.tell()}")
			if chunk_id == b"BKHD":
				instance.bhkd = BKHDSection.from_stream(stream, instance.context, 0, None)
				# print(instance.bhkd)
				instance.chunks.append((chunk_id, instance.bhkd))
			elif chunk_id == b"HIRC":
				instance.hirc = HIRCSection.from_stream(stream, instance.context, 0, None)
				# print(instance.hirc)
				instance.chunks.append((chunk_id, instance.hirc))
			elif chunk_id == b"DIDX":
				instance.didx = DIDXSection.from_stream(stream, instance.context, 0, None)
				instance.chunks.append((chunk_id, instance.didx))
			elif chunk_id == b"DATA":
				instance.data = DATASection.from_stream(stream, instance.context, 0, None)
				instance.chunks.append((chunk_id, instance.data))
			elif chunk_id == b'\x00' * len(chunk_id):
				# empty chunk, could be end
				break
			else:
				raise NotImplementedError(f"Unknown chunk {chunk_id}!")
			# see where this chunk should have ended
			desired_end = after_size_pos + instance.chunks[-1][1].length
			if stream.tell() != desired_end:
				logging.info(f"Ended up at bad offset, seeking to desired {desired_end}")
				stream.seek(desired_end)
		# id the pointers
		if instance.hirc:
			for pointer in instance.hirc.hirc_pointers:
				if pointer.id == 2:
					pointer.hash = fmt_hash(pointer.data.didx_id)
		if instance.didx:
			for pointer in instance.didx.data_pointers:
				pointer.data = bytes(instance.data.wem_datas[pointer.data_section_offset: pointer.data_section_offset + pointer.wem_filesize])
				pointer.hash = fmt_hash(pointer.wem_id)
				pointer.pad = b""

	def inject_audio(self, wem_path, wem_id):
		"""Loads wem audio into the container"""
		logging.info("Injecting audio")
		for pointer in self.didx.data_pointers:
			if pointer.hash == wem_id:
				logging.info(f"found a match {pointer.hash}, reading wem data")
				with open(wem_path, "rb") as f:
					pointer.data = f.read()
				break

	def inject_hirc(self, wem_path, wem_id):
		"""Loads wem size into the events container"""
		logging.info("updating hirc data size")
		if self.hirc:
			for pointer in self.hirc.hirc_pointers:
				if pointer.id == 2:
					if pointer.hash == wem_id:
						logging.info(f"found a match {pointer.hash}, updating wem data size")
						pointer.data.wem_length = os.path.getsize(wem_path)
						# print(hirc_pointer.data)
						break

	def __repr__(self):
		s = 'AuxFileContainer'
		for chunk in self.chunks:
			s += '\nchunk ' + chunk.__repr__()
		s += '\n'
		return s

	@classmethod
	def write_fields(cls, stream, instance):
		"""Update representation, then write the container from the internal representation"""
		offset = 0
		if instance.didx:
			for pointer in instance.didx.data_pointers:
				pointer.data_section_offset = offset
				pointer.wem_filesize = len(pointer.data)
				pointer.pad = get_padding(len(pointer.data), alignment=16)
				offset += len(pointer.data + pointer.pad)
		for chunk_id, chunk in instance.chunks:
			if chunk_id == b"DATA":
				continue
			# print(stream.tell(), chunk_id, chunk)
			stream.write(chunk_id)
			chunk.to_stream(chunk, stream, instance.context)
		if instance.hirc:
			# stream.write(bytearray(instance.old_size - stream.tell()))
			# logging.info(f"End of HIRC at {stream.tell()}")
			return
		if not instance.didx.data_pointers:
			return
		if instance.data:
			data = b"".join(pointer.data + pointer.pad for pointer in instance.didx.data_pointers)
			stream.write(b"DATA")
			# todo
			stream.write_uint(len(data) - len(pointer.pad))
			stream.write(data)
			# ovl ignores the padding of the last wem
			instance.size_for_ovl = stream.tell() - len(pointer.pad)
		logging.info(f"AUX size for OVL {instance.size_for_ovl}")

