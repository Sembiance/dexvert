from nifgen.formats.ms2.imports import name_type_map
from io import BytesIO
import os
import time
import logging
from copy import copy

import numpy as np

from nifgen.formats.base.compounds.PadAlign import get_padding
from nifgen.formats.ms2.compounds.Ms2InfoHeader import Ms2InfoHeader
from nifgen.formats.ms2.compounds.packing_utils import pack_swizzle, PACKEDVEC_MAX
from nifgen.formats.ms2.enums.CollisionType import CollisionType
from nifgen.formats.ms2.versions import *
from nifgen.io import IoFile
from modules.formats.shared import djb2

logging.basicConfig(level=logging.DEBUG)

BUFFER_NAMES = ("verts", "tris", "uvs", "tri_chunks", "vert_chunks")


class Ms2Context:
	def __init__(self):
		self.version = 0
		self.biosyn = 0

	def __repr__(self):
		return f"{self.version} | {self.biosyn}"


class Ms2File(Ms2InfoHeader, IoFile):

	def __init__(self, ):
		super().__init__(Ms2Context())

	@property
	def game(self):
		return get_game(self.context)[0].value

	@game.setter
	def game(self, game_name):
		set_game(self.context, game_name)
		set_game(self.info, game_name)

	def assign_joints(self, bone_info):
		if self.context.version >= 47:
			assert bone_info.one == 1
		# rearranged in war, possibly related to bone index size change
		# assert bone_info.knownff == -1
		assert bone_info.name_count == bone_info.bind_matrix_count == bone_info.bone_count == bone_info.parents_count == bone_info.enum_count
		assert bone_info.zeros_count == 0 or bone_info.zeros_count == bone_info.name_count
		assert bone_info.zero_0 == bone_info.zero_1 == bone_info.zero_2 == bone_info.zero_3 == 0

		if bone_info.joint_count:
			if not hasattr(bone_info, "joints"):
				logging.warning(f"Joints deactivated for debugging")
				return
			joints = bone_info.joints
			if not joints:
				logging.debug(f"Joints not used")
				return
			for bone_i, joint_info in zip(joints.joint_to_bone, joints.joint_infos):
				# usually, this corresponds - does not do for speedtree but does not matter
				joint_info.bone_name = bone_info.bones[bone_i].name
				if joints.bone_count:
					if joints.joint_infos[joints.bone_to_joint[bone_i]] != joint_info:
						logging.warning(f"bone index [{bone_i}] doesn't point to expected joint info")

	def assign_bone_names(self, bone_info):
		try:
			for name_i, bone in zip(bone_info.name_indices, bone_info.bones):
				bone.name = self.buffer_0.names[name_i]
		except:
			logging.error("Names failed...")

	def load(self, filepath, read_bytes=False, read_editable=False, dump=False):
		start_time = time.time()
		self.filepath = filepath
		self.dir, self.name = os.path.split(os.path.normpath(filepath))
		self.read_editable = read_editable
		logging.debug(f"Reading {self.filepath}")
		with open(filepath, "rb") as stream:
			self.read_fields(stream, self)
			if is_old(self.info):
				self.buffer_1_offset = self.buffer_infos.io_start
			else:
				self.buffer_1_offset = self.models_reader.bone_info_start
			self.buffer_2_offset = self.buffer_1_offset + self.bone_info_size

			# logging.info(f"self.buffer_2_offset {self.buffer_2_offset}")
			# logging.info(self)
			# return
			# logging.debug(f"end of header: {self.buffer_1_offset}")

			logging.debug(f"Vertex buffer starts at {self.buffer_2_offset}")
			for i, bone_info in enumerate(self.models_reader.bone_infos):
				try:
					self.assign_bone_names(bone_info)
					self.assign_joints(bone_info)
				except:
					logging.exception(f"Joints or bones {i} lookup failed")
			try:
				self.lookup_material()
			except:
				logging.exception(f"Material lookup failed")
			if read_bytes:
				stream.seek(self.buffer_0.io_start)
				self.buffer_0_bytes = stream.read(self.buffer_0.io_size)
				stream.seek(self.buffer_1_offset)
				self.buffer_1_bytes = stream.read(self.bone_info_size)
				self.buffer_2_bytes = stream.read()
			try:
				self.load_buffers(filepath, stream, dump)
			except:
				logging.exception(f"Buffer lookup failed")
			if read_editable:
				try:
					self.load_meshes()
				except:
					logging.exception(f"Mesh lookup failed {self}")
		logging.debug(f"Read {self.name} in {time.time() - start_time:.2f} seconds")

	def load_buffers(self, filepath, stream, dump):
		for i, buffer_info in enumerate(self.buffer_infos):
			buffer_info.name = None
			buffer_info.index = i
		# attach the static stream to the right buffer_info
		if self.buffer_infos and self.info.static_buffer_index > -1:
			i = self.info.static_buffer_index
			# hack for DLA, static buffer index is different here
			if self.context.version == 7:
				i = 0
			# ZTUAC does not use static_buffer_index eg.
			# * vertex_buffer_count = 4
			# * static_buffer_index = 3
			# all four buffer_infos use modelstream files, and ms2 just has names and bones buffers
			if self.context.version != 13:
				static_buffer_info = self.buffer_infos[i]
				stream.seek(self.buffer_2_offset)
				static_buffer_info.name = "STATIC"
				static_buffer_info.path = filepath
				self.attach_streams(static_buffer_info, stream, dump=dump)
		# attach the streams to all other buffer_infos
		streams = [buffer_info for buffer_info in self.buffer_infos if buffer_info.name != "STATIC"]
		for buffer_info, modelstream_name in zip(streams, self.modelstream_names):
			buffer_info.name = modelstream_name
			buffer_info.path = os.path.join(self.dir, buffer_info.name)
			logging.debug(f"Loading {buffer_info.path}")
			with open(buffer_info.path, "rb") as modelstream_reader:
				self.attach_streams(buffer_info, modelstream_reader, dump=dump)

	def attach_streams(self, buffer_info, in_stream=None, dump=False):
		"""Attaches streams to a buffer info for each section, and fills them if an input stream is provided"""
		logging.info(f"Attaching streams to {buffer_info.name}")
		for buffer_name in BUFFER_NAMES:
			if in_stream:
				buff_size = getattr(buffer_info, f"{buffer_name}_size")
				# create a set to be able to guess the size of any entry
				setattr(buffer_info, f"{buffer_name}_offsets", {buff_size})
				logging.debug(f"Loading {buffer_name} size {buff_size} at {in_stream.tell()}")
				b = in_stream.read(buff_size)
				# dump each for easy debugging
				if dump:
					with open(f"{buffer_info.path}_{buffer_name}.dmp", "wb") as f:
						f.write(b)
			else:
				b = b""
			# attach a reader with the bytes we have read to the buffer_info
			setattr(buffer_info, buffer_name, BytesIO(b))

	def load_meshes(self):
		for model_info in self.model_infos:
			logging.debug(f"Loading mesh data for {model_info.name}")
			for wrapper in model_info.model.meshes:
				wrapper.mesh.assign_buffer_info(self.buffer_infos)
				if hasattr(wrapper.mesh, "uv_offset"):
					wrapper.mesh.buffer_info.uvs_offsets.add(wrapper.mesh.uv_offset)
			if is_old(self.info):
				pack_base = 512
			else:
				pack_base = model_info.pack_base
			try:
				for i, wrapper in enumerate(model_info.model.meshes):
					logging.info(f"Populating mesh {i}")
					wrapper.mesh.populate(pack_base)
				# logging.info(f"Populating mesh worked {model_info}, {model_info.model}")
			except:
				logging.exception(f"Populating mesh failed for model {model_info}, {model_info.model}")

	def name_used(self, new_name):
		for model_info in self.model_infos:
			if model_info.name == new_name:
				return True

	def rename_file(self, old, new):
		logging.info(f"Renaming .mdl2s in {self.name}")
		for model_info in self.model_infos:
			if model_info.name == old:
				model_info.name = new

	def remove(self, mdl2_names):
		logging.info(f"Removing {len(mdl2_names)} .mdl2 files in {self.name}")
		for model_info in reversed(self.model_infos):
			if model_info.name in mdl2_names:
				self.model_infos.remove(model_info)

	def duplicate(self, mdl2_names):
		logging.info(f"Duplicating {len(mdl2_names)} .mdl2 files in {self.name}")
		for model_info in reversed(self.model_infos):
			if model_info.name in mdl2_names:
				model_info_copy = copy(model_info)
				# add as many suffixes as needed to make new_name unique
				self.make_name_unique(model_info_copy)
				self.model_infos.append(model_info_copy)
		self.model_infos.sort(key=lambda model_info: model_info.name)

	def make_name_unique(self, model_info_copy):
		new_name = model_info_copy.name
		while self.name_used(new_name):
			new_name = f"{new_name}_copy"
		model_info_copy.name = new_name

	def rename(self, name_tups):
		"""Renames strings in the main name buffer"""
		logging.info(f"Renaming in {self.name}")

		for model_info in self.model_infos:
			for material in model_info.model.materials:
				material.name = self._rename(material.name, name_tups)
			if model_info.bone_info:
				bi = model_info.bone_info
				for bone in bi.bones:
					bone.name = self._rename(bone.name, name_tups)
				ji = bi.joints
				if ji:
					for joint_info in ji.joint_infos:
						joint_info.bone_name = self._rename(joint_info.bone_name, name_tups)

	def _rename(self, s, name_tups):
		# first a cases sensitive pass
		for old, new in name_tups:
			if old in s:
				logging.debug(f"Match for '{old}' in '{s}'")
				s = s.replace(old, new)
		for old, new in name_tups:
			if old.lower() in s.lower():
				logging.debug(f"Case-insensitive match '{old}' in '{s}'")
				s = s.lower().replace(old, new)
		return s

	def get_name_index(self, name):
		if name not in self.buffer_0.names:
			self.buffer_0.names.append(name)
		return self.buffer_0.names.index(name)

	def update_names(self):
		logging.info("Updating MS2 name buffer")
		self.mdl_2_names.clear()
		self.buffer_0.names.clear()
		for model_info in self.model_infos:
			self.mdl_2_names.append(model_info.name)
			for material in model_info.model.materials:
				material.name_index = self.get_name_index(material.name)
			if model_info.bone_info:
				for bone_index, bone in enumerate(model_info.bone_info.bones):
					model_info.bone_info.name_indices[bone_index] = self.get_name_index(bone.name)
		# print(self.buffer_0.names)
		logging.info("Updating MS2 name hashes")
		# update hashes from new names
		self.info.name_count = len(self.buffer_0.names)
		self.buffer_0.name_hashes.resize(len(self.buffer_0.names))
		for name_i, name in enumerate(self.buffer_0.names):
			self.buffer_0.name_hashes[name_i] = djb2(name.lower())

	def update_buffer_0_bytes(self):
		with BytesIO() as temp_writer:
			self.buffer_0.to_stream(self.buffer_0, temp_writer, self.context)
			self.buffer_0_bytes = temp_writer.getvalue()

	def update_buffer_1_bytes(self):
		with BytesIO() as temp_bone_writer:
			self.models_reader.to_stream(self.models_reader, temp_bone_writer, self.context)
			self.buffer_1_bytes = temp_bone_writer.getvalue()[self.models_reader.bone_info_start:]
			self.bone_info_size = self.models_reader.bone_info_size

	def update_buffer_2_bytes(self):
		if self.read_editable:
			logging.debug(f"Updating buffer 2")
			# todo - determine how many streams we need and update self.buffer_infos, count, and names
			# first init all writers for the buffers
			for buffer_info in self.buffer_infos:
				self.attach_streams(buffer_info)
			# now store each model
			for model_info in self.model_infos:
				logging.debug(f"Storing {model_info.name}")
				# update ModelInfo
				model_info.num_materials = len(model_info.model.materials)
				model_info.num_lods = len(model_info.model.lods)
				model_info.num_objects = len(model_info.model.objects)
				model_info.num_meshes = len(model_info.model.meshes)
				# write each mesh's data blocks to the right temporary buffer
				for wrapper in model_info.model.meshes:
					wrapper.mesh.assign_buffer_info(self.buffer_infos)
					wrapper.mesh.write_data()
				# update LodInfo
				logging.debug(f"Updating lod vertex counts...")
				for lod in model_info.model.lods:
					lod.vertex_count = sum(wrapper.mesh.vertex_count for wrapper in lod.meshes)
					lod.tri_index_count = sum(wrapper.mesh.tri_index_count for wrapper in lod.meshes)
			# modify buffer size
			for buffer_info in self.buffer_infos:
				# get bytes from IO obj, pad, and update size in BufferInfo
				for buffer_name in BUFFER_NAMES:
					buff = getattr(buffer_info, buffer_name)
					buff_bytes = self.get_bytes(buff)
					setattr(buffer_info, f"{buffer_name}_size", len(buff_bytes))
				
			# store static buffer
			if self.buffer_infos and self.info.static_buffer_index > -1:
				buffer_info = self.buffer_infos[self.info.static_buffer_index]
				self.buffer_2_bytes = self.get_all_bytes(buffer_info)
			else:
				# Assing an empty buffer, maybe it is better to add an 'if attrib' in the saving?
				self.buffer_2_bytes = b""

	@staticmethod
	def get_bytes(buffer_reader):
		buff_bytes = buffer_reader.getvalue()
		buff_bytes += get_padding(len(buff_bytes), alignment=16)
		return buff_bytes

	def get_all_bytes(self, buffer_info):
		return b"".join(self.get_bytes(getattr(buffer_info, b_name)) for b_name in BUFFER_NAMES)

	@property
	def buffers(self):
		yield self.buffer_0_bytes
		yield self.buffer_1_bytes
		# PZ uses only two buffers in this case, JWE2 keeps an empty third buffer
		if not self.buffer_2_bytes and is_pz(self.info):
			return
		yield self.buffer_2_bytes

	def save(self, filepath):
		self.dir, self.name = os.path.split(os.path.normpath(filepath))
		# for modelstreams, trailing _ is ignored
		self.basename = os.path.splitext(self.name)[0].rstrip("_")
		logging.info("Pre-writing buffers")
		# just a quick hack to support WH
		for model_info in self.model_infos:
			if hasattr(model_info.bone_info, "bone_limits"):
				if self.context.version < 53:
					model_info.bone_info.bone_limits.index = 255
		self.info.mdl_2_count = len(self.model_infos)
		self.update_names()
		self.update_buffer_0_bytes()
		self.update_buffer_1_bytes()
		self.update_buffer_2_bytes()
		# save multiple buffer_infos
		streams = [buffer_info for buffer_info in self.buffer_infos if buffer_info.name != "STATIC"]
		for i, buffer_info in enumerate(streams):
			assert buffer_info.name.endswith(".model2stream")
			# update the modelstram name incase
			buffer_info.name = f"{self.basename}{i}.model2stream"
			# write external .model2stream files
			buffer_info.path = os.path.join(self.dir, buffer_info.name)
			with open(buffer_info.path, "wb") as f:
				f.write(self.get_all_bytes(buffer_info))
		self.modelstream_names[:] = [buffer_info.name for buffer_info in streams]
		logging.info(f"Writing to {filepath}")
		with open(filepath, "wb") as stream:
			self.write_fields(stream, self)
			stream.write(self.buffer_2_bytes)

	def lookup_material(self):
		for name, model_info in zip(self.mdl_2_names, self.model_infos):
			logging.debug(f"Mapping links for {name}")
			model_info.name = name
			for lod_index, lod in enumerate(model_info.model.lods):
				logging.debug(f"Mapping LOD{lod_index}")
				lod.objects = model_info.model.objects[lod.first_object_index:lod.last_object_index]
				# todo - investigate how duplicate meshes are handled for the lod's vertex count0
				lod.meshes = tuple(model_info.model.meshes[obj.mesh_index] for obj in lod.objects)
				for obj in lod.objects:
					try:
						material = model_info.model.materials[obj.material_index]
						material.name = self.buffer_0.names[material.name_index]
						obj.mesh = model_info.model.meshes[obj.mesh_index].mesh
						obj.material = material
						flag = int(obj.mesh.flag) if hasattr(obj.mesh, "flag") else None
						logging.debug(
							f"Mesh: {obj.mesh_index} Material: {material.name} Blend Mode: {material.blend_mode} "
							f"Lod: {obj.mesh.poweroftwo} Flag: {flag}")
					except:
						logging.exception(f"Couldn't match material {obj.material_index} to mesh {obj.mesh_index}")

	def clear(self):
		for model_info in self.model_infos:
			model_info.model.materials.clear()
			model_info.model.lods.clear()
			model_info.model.objects.clear()
			model_info.model.meshes.clear()


if __name__ == "__main__":
	# import math
	# a1 = [(8.0, 7.629452738910913e-06), (512.0, 0.0004885197849944234), (1024.0, 0.0009775171056389809),
	#  (2048.0, 0.001956947147846222), (4096.0, 0.003921568859368563)]
	# for pack_base, scale in a1:
	# 	quad = 1.2285932501219967e-9 + 9.536674737032024e-7 * pack_base + 9.14657200199282e-13 * math.pow(pack_base, 2)
	# 	# quad = 1.229e-9 + 9.537e-7 * pack_base + 9.147e-13 * math.pow(pack_base, 2)
	# 	lin = pack_base * 9.57536917458211E-07
	# 	d = (1 + pack_base) * pack_base / PACKEDVEC_MAX - pack_base
	# 	d = 1 / np.round((0 + pack_base) / pack_base * PACKEDVEC_MAX - pack_base)
	# 	# print(f"pack_base {pack_base}, scale {scale}, quad {quad}, lin {lin}, (quad-scale) {quad-scale}, (lin-scale) {lin-scale}" )
	# 	# print(f"pack_base {pack_base}, scale {scale}, quad {quad}, lin {lin}, d {d}" )
	#
	# 	base_exp = math.log2(pack_base)
	# 	error = 4 ** (base_exp-10.0)
	# 	scale2 = (error + pack_base) / PACKEDVEC_MAX
	# 	# scale_a = get_scale2(pack_base)
	# 	# scale_b = get_scale_long(pack_base)
	# 	# print(scale_a, scale_b, scale_b == scale_a)
	# 	# print(i, pack_base, base_exp, error, scale)
	# 	# print(pack_base, PACKEDVEC_MAX * scale, PACKEDVEC_MAX * scale - pack_base, scale)
	# 	# print(pack_base, scale, scale2, scale2-scale, quad, quad-scale)
	# 	# print(f"pack_base {pack_base}, scale {scale}, scale2 {scale2}, quad {quad}, (scale2-scale) {scale2-scale}, (quad-scale) {quad-scale}" )
	# 	# error = PACKEDVEC_MAX * scale - pack_base
	# 	# error + pack_base = PACKEDVEC_MAX * scale
	# 	# (error + pack_base) / PACKEDVEC_MAX = scale
	# # (scale + pack_base) / pack_base = 1.0
	# for i in range(0, 16):
	# 	pack_base = 2**i
	# 	base_exp = math.log2(pack_base)
	# 	error = 4 ** (base_exp-10.0)
	# 	scale = (error + pack_base) / PACKEDVEC_MAX
	# 	print(i, pack_base, base_exp, error, scale)
	# for i in range(-2, 3):
	# 	print(i, 4**i)
	# 	# 1024 = 2**10 == 1 = 4 ** 0

	m = Ms2File()
	# m.load("C:/Users/arnfi/Desktop/camerabone_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/FR_GrandCarousel.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/SP_Grave_Stones.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/Coding/Frontier/PC ovls/walker_export/SP_Scarecrow not working atm.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/Coding/Frontier/Warhammer/Annihilator/annihilatormodels.ms2", read_editable=True)
	m.load("C:/Users/arnfi/Desktop/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/janitormale_.ms2", read_editable=True)
	print(m)
	# m.save("C:/Users/arnfi/Desktop/test.ms2")
	# m.load("C:/Users/arnfi/Desktop/jwe2/pyro/export/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/pyro/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/moros/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/ankylodocus.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/pteranodon_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/rabbit_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/bush_berry_bear.ms2", read_editable=True)
	# print(m.models_reader.bone_infos[0])
	# print(m)
	# m.load("C:/Users/arnfi/Desktop/Coding/Frontier/MeshCollision/JWE2/CharacterScale/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/Coding/Frontier/MeshCollision/PZ/widgetball_test_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/Coding/Frontier/MeshCollision/PZ/CM_Common_Roofs.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/Coding/Frontier/MeshCollision/JWE2dev/groundplane_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/Coding/Frontier/MeshCollision/JWE2dev/footplantingtest_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/export/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/hazard_ceilingfan_.ms2", read_editable=True)
	# print(m.models_reader.bone_infos[0])
	# mods = set()
	# flags = set()
	# for bone_info in m.models_reader.bone_infos:
	# 	# print(bone_info)
	# 	if bone_info.joint_count:
	# 		for ji in bone_info.joints.joint_infos:
	# 			for hc in ji.hitchecks:
	# 				if hc.dtype == CollisionType.MESH_COLLISION:
	# 					print(hc)
	# for mo in m.model_infos:
	# 	# print(mo.bone_info)
	# 	# print(mo.model.lods)
	# 	# print(mo.model.objects)
	# 	for i, me in enumerate(mo.model.meshes):
	# 		# print(i, me)
	# # 		# for t, v in zip(me.mesh.tri_chunks, me.mesh.vert_chunks):
	# # 		# 	t.rot.a = 1.0
	# # 		# 	t.rot.x = t.rot.y = t.rot.z = 0.0
	# # 		# 	t.loc.x = t.loc.y = t.loc.z = 0.0
	# 		for t, v in zip(me.mesh.tri_chunks, me.mesh.vert_chunks):
	# 			# print(t, v)
	# 			print(v)
	# 			s = v.pack_base / v.scale
	# 			print(s)
	# 			break
	# 			# flags.add(tuple(v.flags))
	# 		print(flags)
			# 	pass
			# 	# print(i, t.tris_offset)
			# 	# print(i, v.vertex_offset % 16)
			# 	mods.add(v.vertex_offset % 16)
	# 		flags.add(me.mesh.flag)
	# print(mods)
			# if i in (12, 13, 14):
			# if i in (12, ):
			# 	print(i)
			# 	for ch_i in range(10):
			# 		tri_ch = me.mesh.tri_chunks[ch_i]
			# 		vert_ch = me.mesh.vert_chunks[ch_i]
			# 		# print(tri_ch)
			# 		av = np.mean(vert_ch.normals, axis=0)
			# 		md = np.median(vert_ch.normals, axis=0)
			# 		# print(tri_ch.rot, pack_swizzle(av / np.linalg.norm(av)), pack_swizzle(md / np.linalg.norm(md)), vert_ch.normals[0])
			# 		print(tri_ch.rot, pack_swizzle(vert_ch.normals[0]), pack_swizzle(vert_ch.normals[-1]), )
			# 		print(np.linalg.norm((tri_ch.rot.x, tri_ch.rot.y, tri_ch.rot.z, )), )
	# m.save("C:/Users/arnfi/Desktop/export/models.ms2")

	# m.load("C:/Users/arnfi/Desktop/park_captainhook_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/export/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/baryo/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/park_snowwhite_.ms2", read_editable=True)
	# print(m.models_reader.bone_infos[0].bone_names)
	# print(m.buffer_0.names[142])
	# m.load("C:/Users/arnfi/Desktop/shop_mainstreet_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/c_bz_shipparts_.ms2", read_editable=True)
	# print(m)
	# m.load("C:/Users/arnfi/Desktop/nile_lechwe_male_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/tree_palm_coconut_desert.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/export/tree_palm_coconut_desert.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/export/tree_palm_coconut.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/rhinoblack_female_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/caribou/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/models.ms2", read_editable=True)
	# m.load("C:/Program Files (x86)/Steam/steamapps/common/Jurassic World Evolution 2/Win64/ovldata/walker_export/ContentPDLC3/Dinosaurs/Land/Therizinosaurus/Therizinosaurus/models.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/pine/tree_pine_blackspruce.ms2", read_editable=True)

	# m.load("C:/Users/arnfi/Desktop/tree_palm_coconut_desert.ms2", read_editable=True)
	# for model_info in m.model_infos:
	# 	for w in model_info.model.meshes:
	# 		me = w.mesh
	# 		me.vertices[:, 1] += np.sin(np.pi * me.vertices[:, 2] * 0.2) * 2
	# 		# me.vertices[:, 2] *= 2
	# 		me.pack_verts()
	# m.save("C:/Users/arnfi/Desktop/export/tree_palm_coconut_desert.ms2")

	# m.load("C:/Users/arnfi/Desktop/dilophosaurus.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/diplodocus.ms2", read_editable=True)
	# m.save("C:/Users/arnfi/Desktop/models.ms2")
	# m.load("C:/Users/arnfi/Desktop/paths_new/strips.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/bornean_orangutan_male_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/acacia/tree_acacia_umbrella_thorn.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/scimitar_horned_oryx_female_.ms2", read_editable=True)
	# m.load("C:/Users/arnfi/Desktop/quetz.ms2", read_editable=True)
	# m.save("C:/Users/arnfi/Desktop/models.ms2")
	# print(m)
	# print(m.model_infos[1].bone_info.joints.joint_infos)
