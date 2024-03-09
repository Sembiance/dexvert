from nifgen.formats.bani.imports import name_type_map
from nifgen.formats.bani.compounds.BanisInfoHeader import BanisInfoHeader
from nifgen.io import IoFile
import os

import math
import numpy as np

# +-
rot_range = 180
short_range = 32767
ushort_range = 65535

def export_key(key):
	# this seems to be a modulo equivalent
	k = [x for x in key]
	for i in range(3):
		# if k[i] < -180:
		# k[i]+= 360
		if k[i] < -90:
			k[i] = 360 - k[i]
	k[0] -= 90
	k[2] += 90
	# calculate short
	k = [int(x / 180 * 32768 - 16385) for x in k]
	return k


class BaniContext(object):
	def __init__(self):
		self.version = 0
		self.user_version = 0

	def __repr__(self):
		return f"{self.version} | {self.user_version}"


class BanisFile(BanisInfoHeader, IoFile):
	dt_packed = np.dtype([
		("euler", np.short, (3,)),
		# ("euler", np.ushort, (3,)),
		("loc", np.ushort, (3,)),
	])
	dt_float = np.dtype([
		("euler", np.float32, (3,)),
		("loc", np.float32, (3,)),
	])

	def __init__(self):
		super().__init__(BaniContext())

	def load(self, filepath):
		# store file name for later
		self.file = filepath
		self.dir, self.basename = os.path.split(filepath)
		self.path_no_ext = os.path.splitext(self.file)[0]

		with open(filepath, "rb") as stream:
			self.read_fields(stream, self)
			keys_packed = np.empty(dtype=self.dt_packed, shape=(self.data.num_frames, self.data.num_bones))
			stream.readinto(keys_packed)
			keys_float = keys_packed.astype(self.dt_float)
			print(keys_packed[0, :, ])
			keys_float["euler"] = keys_float["euler"] / short_range * rot_range
			# keys_float["euler"] = (keys_float["euler"] - short_range) / short_range * rot_range
			# short
			keys_float["euler"][:, :, 0] += 90.0
			keys_float["euler"][:, :, 1] += 90.0
			keys_float["euler"][:, :, 2] -= 90.0
			# ushort
			# keys_float["euler"][:, :, 0] -= 90.0
			# keys_float["euler"][:, :, 1] -= 90.0
			# keys_float["euler"][:, :, 2] += 90.0
			# [[[89.9945  1.0162 89.9945]
			#   [89.978  -2.7026 90.5548]
			#   [89.978  -2.7026 90.5548]

			keys_float["loc"] = keys_float["loc"] * self.data.loc_scale + self.data.loc_min
		# print(keys_float["euler"])
		print(keys_float[0, :, ])
		print(self)
		# assign keys to bani data
		for bani in self.anims:
			bani.keys = keys_float[bani.data.read_start_frame: bani.data.read_start_frame + bani.data.num_frames]

	def save(self, filepath):
		self.num_anims = len(self.anims)
		offset = 0
		self.data.num_frames = 0
		for bani in self.anims:
			bani.data.num_frames = len(bani.keys)
			self.data.num_frames += bani.data.num_frames
			bani.data.read_start_frame = offset
			offset += bani.data.num_frames
		# assume all have same bone count
		_num_frames, self.data.num_bones = bani.keys.shape
		self.data.bytes_per_frame = 12
		self.data.bytes_per_bone = self.data.num_bones * self.data.bytes_per_frame
		# reassemble the whole array as floats
		keys_float = np.empty(dtype=self.dt_float, shape=(self.data.num_frames, self.data.num_bones))
		for bani in self.anims:
			keys_float[bani.data.read_start_frame: bani.data.read_start_frame + bani.data.num_frames] = bani.keys

		# cf https://nfrechette.github.io/2016/11/09/anim_compression_range_reduction/
		# choose loc scale to spread loc range across 0 - 65535
		# todo - make 0.0 land on 32767.0, seems to be that way in stock
		self.data.loc_min = np.min(keys_float["loc"])
		self.data.loc_scale = (np.max(keys_float["loc"]) - self.data.loc_min) / ushort_range
		keys_float["loc"] = (keys_float["loc"] - self.data.loc_min) / self.data.loc_scale

		# short
		keys_float["euler"][:, :, 0] -= 90.0
		keys_float["euler"][:, :, 1] -= 90.0
		keys_float["euler"][:, :, 2] += 90.0
		# ushort
		# keys_float["euler"][:, :, 0] += 90.0
		# keys_float["euler"][:, :, 1] += 90.0
		# keys_float["euler"][:, :, 2] -= 90.0
		# wrap if they exceed the valid range
		keys_float["euler"][keys_float["euler"] > rot_range] -= (2*rot_range)
		keys_float["euler"][keys_float["euler"] < -rot_range] += (2*rot_range)
		print(np.min(keys_float["euler"]), np.max(keys_float["euler"]))
		keys_float["euler"] = keys_float["euler"] * short_range / rot_range
		# keys_float["euler"] = keys_float["euler"] * short_range / rot_range + short_range
		print(np.min(keys_float["euler"]), np.max(keys_float["euler"]))
		# round parts separately
		keys_float["euler"].round(out=keys_float["euler"])
		keys_float["loc"].round(out=keys_float["loc"])
		# pack to short
		keys_packed = keys_float.astype(self.dt_packed)
		# print(keys_packed[0, :, ])
		with open(filepath, "wb") as stream:
			self.write_fields(stream, self)
			stream.write(keys_packed.tobytes())
		# print(self.data)


if __name__ == "__main__":
	banis = BanisFile()
	# banis.load("C:/Users/arnfi/Desktop/gila/gila_monster_idles.banisetc1b711e6 - just one anim.banis")
	# # i = np.interp()
	# x = np.linspace(-np.pi, np.pi, banis.num_frames)
	# # sin_dat = (np.sin(x)+1)*32768
	# sin_dat = np.sin(x) * 25000 + 32768
	# banis.keys[:, 7]["loc"][:, 2] = sin_dat
	# # sin2_dat = (np.sin(x)+1)*32768  # for ushort
	# sin2_dat = np.sin(x) * 2000 - 10834
	# # print(sin2_dat)
	#
	# # it does not appear to be the normalized remainder of a quat
	# # for bone in range(banis.num_bones):
	# # 	print(bone)
	# # 	for x, y, z in banis.keys[:, bone]["euler"].astype(dtype=np.float32):
	# # 		print(bone, math.sqrt(x*x+y*y+z*z))
	# # banis.keys[:, 7]["euler"][:, 0] = 0
	# # banis.keys[:, 7]["euler"][:, 2] = 32768
	# # banis.keys[:, 7]["euler"][:, 2] = sin2_dat
	# # 0 = rotate about global X in blender
	# # 1 = rotate about global Z in blender
	# # 2 = rotate about global Y in blender
	# head_keys = banis.keys[:, 7]["euler"][:, 2]
	# banis.save("C:/Users/arnfi/Desktop/gila/gila_monster_idles.banisetc1b711e6.banis")
	# banis.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/banis/food/food_carnivore.banisetfcbde7ca.banis")
	banis.load("C:/Users/arnfi/Desktop/food_carnivore.banisetfcbde7ca.banis")
	banis.save("C:/Users/arnfi/Desktop/food_carnivore.banisetfcbde7ca_test.banis")
	# print(head_keys)
