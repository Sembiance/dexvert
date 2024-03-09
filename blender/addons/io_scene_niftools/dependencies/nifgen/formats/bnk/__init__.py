from nifgen.formats.bnk.imports import name_type_map
from nifgen.formats.bnk.compounds.AuxFileContainer import AuxFileContainer
from nifgen.formats.bnk.compounds.BnkFileContainer import BnkFileContainer
from nifgen.formats.ovl_base import OvlContext
from nifgen.io import IoFile

import os
import logging

from modules.formats.shared import fmt_hash


class BnkFile(BnkFileContainer, IoFile):

	def __init__(self):
		super().__init__(OvlContext())
		self.aux_b = None
		self.aux_b_name_bare = self.aux_b_path = self.aux_s_name_bare = self.aux_s_path = self.bnk_name_bare = self.bnk_dir = self.bnk_name = None
		self.data_map = {}
		# self.s_map = {}

	def load(self, filepath):
		with open(filepath, "rb") as stream:
			self.read_fields(stream, self)
		self.data_map = {}
		# self.s_map = {}
		# alternatively, bnk_name from bnk header
		self.bnk_dir, self.bnk_name = os.path.split(filepath)
		self.bnk_name_bare = os.path.splitext(self.bnk_name)[0]
		if self.bnk_header.external_s_suffix:
			self.aux_s_name_bare, self.aux_s_path = self.get_aux_path("s")
			with open(self.aux_s_path, "rb") as f:
				for i, stream_info in enumerate(self.bnk_header.streams):
					f.seek(stream_info.offset)
					id_hash = fmt_hash(stream_info.event_id)
					self.data_map[id_hash] = f.read(stream_info.size), self.aux_s_name_bare
		# since the b aux can be originally internal as a buffer, or an external file, we just check if the file now exists
		self.aux_b_name_bare, self.aux_b_path = self.get_aux_path("b")
		if self.aux_b_name_bare:
			self.aux_b = AuxFile()
			self.aux_b.load(self.aux_b_path)
			if self.aux_b.didx:
				for pointer in self.aux_b.didx.data_pointers:
					self.data_map[pointer.hash] = pointer.data, self.aux_b_name_bare

	def get_aux_path(self, suffix):
		# no way of knowing the ovl prefix here
		ovl_basename = ""
		end_str = f"{ovl_basename}_{self.bnk_name_bare}_bnk_{suffix}.aux"
		logging.debug(f"Looking for {end_str} in {self.bnk_dir}")
		aux_file_names = [f for f in os.listdir(self.bnk_dir) if f.lower().endswith(end_str)]
		# print(os.listdir(bnk_dir))
		# print(aux_file_names)
		# aux_path = os.path.join(bnk_dir, f"{ovl_basename}_{bnk_name}_bnk_{suffix}.aux")
		if not aux_file_names:
			logging.error(f"AUX file '{suffix}' expected in {self.bnk_dir}!")
			return None, None
		if len(aux_file_names) > 1:
			logging.warning(f"Multiple aux files qualified!")
		aux_file_name = aux_file_names[0]
		aux_file_name_bare = os.path.splitext(aux_file_name)[0]
		aux_path = os.path.join(self.bnk_dir, aux_file_name)
		return aux_file_name_bare, aux_path

	def save(self, filepath):
		self.old_size = os.path.getsize(filepath)
		with open(filepath, "wb") as stream:
			self.write_fields(stream, self)


class AuxFile(AuxFileContainer, IoFile):

	def __init__(self):
		super().__init__(OvlContext())

	def load(self, filepath):
		with open(filepath, "rb") as stream:
			self.read_fields(stream, self)

	def save(self, filepath):
		self.old_size = os.path.getsize(filepath)
		with open(filepath, "wb") as stream:
			self.write_fields(stream, self)


if __name__ == "__main__":
	# bnk = BnkFile()
	# bnk.load("C:/Users/arnfi/Desktop/Coding/ovl/aux files/dlc_dingo_dlc_dingo_media_bnk_B.aux")
	# print(bnk)
	bnk = BnkFile()
	bnk.load("C:/Users/arnfi/Desktop/Coding/ovl/aux files/music_vehicleradio_events.bnk")
	print(bnk)
