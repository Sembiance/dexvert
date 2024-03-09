import logging
import math

from nifgen.array import Array
from nifgen.formats.ms2.compounds.VertChunk import VertChunk
from nifgen.formats.ms2.compounds.TriChunk import TriChunk
from nifgen.formats.ms2.compounds.packing_utils import *
from nifgen.formats.ms2.enums.MeshFormat import MeshFormat
from plugin.utils.tristrip import triangulate


from nifgen.array import Array
from nifgen.formats.ms2.compounds.MeshData import MeshData
from nifgen.formats.ms2.imports import name_type_map


class ChunkedMesh(MeshData):

	"""
	JWE2 after Biosyn update - 48 bytes incl. inheritance
	"""

	__name__ = 'ChunkedMesh'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# start index into list of verts / tris chunks
		self.chunks_offset = name_type_map['Uint'](self.context, 0, None)

		# count of verts / tris chunks
		self.chunks_count = name_type_map['Uint'](self.context, 0, None)
		self.tris_count = name_type_map['Uint'](self.context, 0, None)

		# num verts in mesh
		self.vertex_count = name_type_map['Uint'](self.context, 0, None)

		# unk, may be used in other models
		self.zero_1 = name_type_map['Uint64'](self.context, 0, None)

		# power of 2 increasing with lod index
		self.poweroftwo = name_type_map['Uint'](self.context, 0, None)

		# some floats, purpose unknown
		self.unk_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# seen 1 or 13
		self.flag = name_type_map['ChunkedModelFlag'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'chunks_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'chunks_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tris_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'poweroftwo', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None), (None, None)
		yield 'flag', name_type_map['ChunkedModelFlag'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'chunks_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'chunks_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'tris_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'poweroftwo', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None)
		yield 'flag', name_type_map['ChunkedModelFlag'], (0, None), (False, None)

	# @property
	def get_stream_index(self):
		# logging.debug(f"Using stream {self.stream_info.pool_index}")
		return self.stream_info.pool_index

	@property
	def tris_address(self):
		# this assumes that chunks are sorted by tris_offset, not guaranteed to be always true
		return self.tri_chunks[0].tris_offset

	def read_tris(self):
		pass

	def read_tris_bio(self):
		# read all tri indices for this mesh
		self.buffer_info.tris.seek(self.tris_address)
		index_count = self.tris_count * 3  # // self.shell_count
		# logging.info(f"Reading {index_count} indices at {self.buffer_info.tris.tell()}")
		_tri_indices = np.empty(dtype=np.uint8, shape=index_count)
		self.buffer_info.tris.readinto(_tri_indices)
		self.tri_indices = _tri_indices.astype(np.uint32)

	@staticmethod
	def pr_indices(input_list, indices, msg):
		print(f"\n{msg}")
		for i, inp in enumerate(input_list):
			if i in indices:
				print(f"{i} = {inp}")

	@property
	def tri_chunks_address(self):
		size_of_chunk = 64
		return self.chunks_offset * size_of_chunk

	@property
	def vert_chunks_address(self):
		size_of_chunk = 16
		return self.chunks_offset * size_of_chunk

	def read_verts(self):
		# logging.debug(self)
		self.read_chunk_infos()
		# check first vert_chunk
		vert_chunk = self.vert_chunks[0]
		self.mesh_format = vert_chunk.weights_flag.mesh_format
		self.update_dtype()
		self.init_arrays()

		first_tris_offs = self.tri_chunks[0].tris_offset
		offs = 0

		self.read_tris_bio()
		self.weights_info = {}
		self.face_maps = {}
		self.bones_sets = []
		mesh_formats = set()
		for i, (tri_chunk, vert_chunk) in enumerate(zip(self.tri_chunks, self.vert_chunks)):
			# bones_per_chunk = set()
			# logging.debug(f"{i}, {tri_chunk}, {vert_chunk}")
			#logging.debug(f"{i}, {vert_chunk.weights_flag}")

			# these sometimes correspond but not always
			# logging.info(f"chunk {i} tris at {tri_chunk.tris_offset}, weights_flag {vert_chunk.weights_flag}")

			self.buffer_info.verts.seek(vert_chunk.vertex_offset)
			# logging.info(f"tri_chunk {i} {tri_chunk.tris_offset} {tri_chunk.tris_count} tris")
			# logging.info(f"packed_verts {i} start {self.buffer_info.verts.tell()}, count {vert_chunk.vertex_count}")

			v_slice = np.s_[offs: offs + vert_chunk.vertex_count]
			self.init_vert_chunk_arrays(v_slice, vert_chunk)
			tris_start = tri_chunk.tris_offset - first_tris_offs
			tri_chunk.tri_indices = self.tri_indices[tris_start: tris_start+tri_chunk.tris_count * 3]
			mesh_formats.add(vert_chunk.weights_flag.mesh_format)
			try:
				if vert_chunk.weights_flag.mesh_format in (MeshFormat.SEPARATE, MeshFormat.UNK_FMT):
					self.buffer_info.verts.readinto(vert_chunk.packed_verts)
					# decode and store position
					unpack_int64_vector(vert_chunk.packed_verts, vert_chunk.vertices, vert_chunk.negate_bitangents)
					scale_unpack_vectorized(vert_chunk.vertices, vert_chunk.pack_base)

					self.read_weights(vert_chunk, offs)
					# read uv, normals etc
					# logging.info(f"meta {i} start {self.buffer_info.verts.tell()}")
					self.buffer_info.verts.readinto(vert_chunk.meta)

				elif vert_chunk.weights_flag.mesh_format in (MeshFormat.INTERLEAVED_32, MeshFormat.INTERLEAVED_48):
					# interleaved vertex array, meta includes all extra data
					self.buffer_info.verts.readinto(vert_chunk.meta)
					# store position
					vert_chunk.vertices[:] = vert_chunk.meta["pos"]
					self.read_weights(vert_chunk, offs)
				else:
					raise AttributeError(f"Unsupported weights_flag.mesh_format {vert_chunk.weights_flag.mesh_format}")
				# store chunk's meta data in mesh's array
				vert_chunk.uvs[:] = vert_chunk.meta["uvs"]
				vert_chunk.colors[:] = vert_chunk.meta["colors"]
				vert_chunk.normals[:, :2] = vert_chunk.meta["normal_oct"]
				vert_chunk.tangents[:, :2] = vert_chunk.meta["tangent_oct"]

				if vert_chunk.weights_flag.mesh_format in (MeshFormat.INTERLEAVED_32,):
					vert_chunk.shapekeys[:] = vert_chunk.meta["shapekey"]
					vert_chunk.floats[:] = vert_chunk.meta["floats"]
			except:
				logging.exception(f"Chunk {i} failed")
			# create absolute vertex indices for the total mesh
			tri_chunk.tri_indices += offs
			offs += vert_chunk.vertex_count

			# ##### temporary debugging stuff
			# self.bones_sets.append((vert_chunk.vertex_count, bones_per_chunk))
			# prep face maps
			_weights = f"_weights" if vert_chunk.weights_flag.has_weights else ""
			id_str = f"{i:03}{_weights}"
			self.face_maps[id_str] = list(range(tris_start // 3, tris_start // 3 + tri_chunk.tris_count))
		# since malta dlc, one mesh can have several mesh formats
		# assert len(mesh_formats) == 1
		# logging.info(self.bones_sets)
		# max_verts = max(vert_chunk.vertex_count for vert_chunk in self.vert_chunks)
		# logging.debug(f"max_verts {max_verts}")

		# slower
		# decode_oct(vert_chunk.tangents, vert_chunk.meta["tangent_oct"])
		# decode_oct(vert_chunk.normals, vert_chunk.meta["normal_oct"])
		oct_to_vec3(self.normals)
		oct_to_vec3(self.tangents)
		unpack_swizzle_vectorized(self.vertices)
		unpack_swizzle_vectorized(self.shapekeys)
		unpack_swizzle_vectorized(self.normals)
		unpack_swizzle_vectorized(self.tangents)
		unpack_ubyte_color(self.colors)
		# currently, known uses of Interleaved48 use impostor uv atlas
		if vert_chunk.weights_flag.mesh_format == MeshFormat.INTERLEAVED_48:
			unpack_ushort_vector_impostor(self.uvs)
		else:
			unpack_ushort_vector(self.uvs)
		self.fur_length = 0.0
		# just a sanity check
		assert self.vertex_count == sum(o.vertex_count for o in self.vert_chunks)
		# for debugging
		# for vertex_index, res in enumerate(self.negate_bitangents):
		# 	self.add_to_weights(f"negate_bitangents", vertex_index, res)

	def init_vert_chunk_arrays(self, v_slice, vert_chunk):
		vert_chunk.packed_verts = None
		vert_chunk.weights = None
		vert_chunk.meta = None
		# views into main array
		vert_chunk.vertices = self.vertices[v_slice]
		vert_chunk.shapekeys = self.shapekeys[v_slice]
		vert_chunk.negate_bitangents = self.negate_bitangents[v_slice]
		vert_chunk.colors = self.colors[v_slice]
		vert_chunk.uvs = self.uvs[v_slice]
		vert_chunk.normals = self.normals[v_slice]
		vert_chunk.tangents = self.tangents[v_slice]
		vert_chunk.floats = self.floats[v_slice]
		chunk_fmt = vert_chunk.weights_flag.mesh_format
		if chunk_fmt in (MeshFormat.SEPARATE, MeshFormat.UNK_FMT):
			# todo - once stable, change back to empty
			vert_chunk.packed_verts = np.zeros(dtype=np.int64, shape=vert_chunk.vertex_count)
			vert_chunk.weights = np.zeros(dtype=self.dt_weights, shape=vert_chunk.vertex_count)
			vert_chunk.meta = np.zeros(dtype=self.dts[chunk_fmt], shape=vert_chunk.vertex_count)
		elif chunk_fmt in (MeshFormat.INTERLEAVED_32, MeshFormat.INTERLEAVED_48):
			# interleaved vertex array, meta includes all extra data
			vert_chunk.meta = np.zeros(dtype=self.dts[chunk_fmt], shape=vert_chunk.vertex_count)

	@property
	def dt(self):
		return self.dts[self.mesh_format]

	def read_weights(self, vert_chunk, offs):
		# check if weights chunk is present
		if vert_chunk.weights_flag.has_weights:
			# read for each vertex
			if self.context.version >= 52:
				# not sure if uint or int, but seems to work!
				# vert_chunk.weights may have to be cast to uint16 because of the new 10 bit precision
				# however, there are no meshes that make use of the extra precision as of 2022-12
				vert_chunk.packed_weights = np.zeros(dtype=np.uint64, shape=vert_chunk.vertex_count)
				self.buffer_info.verts.readinto(vert_chunk.packed_weights)
				# logging.info(vert_chunk.packed_weights)
				unpack_int64_weights(vert_chunk.packed_weights, vert_chunk.weights)
			else:
				self.buffer_info.verts.readinto(vert_chunk.weights)
			# logging.info(vert_chunk.weights)
			for vertex_index, (bone_indices, bone_weights) in enumerate(
					zip(vert_chunk.weights["bone ids"], vert_chunk.weights["bone weights"] / 255)):
				for bone_index, weight in zip(bone_indices, bone_weights):
					if weight > 0.0:
						self.add_to_weights(bone_index, vertex_index + offs, weight)

		# 			bones_per_chunk.add(bone_index)
		# logging.info(f"Length set {len(bones_per_chunk)}")
		else:
			# use the chunk's bone index for each vertex in chunk
			for vertex_index in range(vert_chunk.vertex_count):
				self.add_to_weights(vert_chunk.weights_flag.bone_index, vertex_index + offs, 1.0)
		# bones_per_chunk.add(vert_chunk.weights_flag.bone_index)

	def update_dtype(self):
		# prepare descriptions of the dtypes
		_normal_tangent_oct = (("normal_oct", np.ubyte, (2,)), ("tangent_oct", np.ubyte, (2,)))
		# per-vertex weights may or may not be used in a given chunk
		dt_weights = [
			("bone ids", np.ubyte, (4,)),
			("bone weights", np.ubyte, (4,)),
		]
		# 16 bytes of metadata that follows the vertices array
		dt_separate = [
			*_normal_tangent_oct,
			("uvs", np.ushort, (2, 2)),
			("colors", np.ubyte, 4)
		]
		# 32 bytes per vertex, with all data interleaved
		dt_interleaved32 = [
			("pos", np.float16, (3,)),
			("shapekey", np.float16, (3,)),  # used for lod fading
			("floats", np.float16, 4),
			*_normal_tangent_oct,
			("uvs", np.ushort, (1, 2)),
			("colors", np.ubyte, 4)
		]
		# 48 bytes per vertex, with all data interleaved, totally different from older 48 bytes vert
		dt_interleaved48 = [
			("pos", np.float16, (3,)),
			("one", np.ubyte),  # not sure
			("zero", np.ubyte),  # may be bone index
			*_normal_tangent_oct,
			("colors", np.ubyte, 4),  # zero, may be colors
			("uvs", np.ushort, (8, 2)),
		]
		self.dts = {}
		self.dts[MeshFormat.SEPARATE] = np.dtype(dt_separate)
		self.dts[MeshFormat.UNK_FMT] = np.dtype(dt_separate)
		self.dts[MeshFormat.INTERLEAVED_32] = np.dtype(dt_interleaved32)
		self.dts[MeshFormat.INTERLEAVED_48] = np.dtype(dt_interleaved48)
		self.dt_weights = np.dtype(dt_weights)

	def read_chunk_infos(self):
		self.buffer_info.tri_chunks.seek(self.tri_chunks_address)
		self.tri_chunks = Array.from_stream(self.buffer_info.tri_chunks, self.context, 0, None, (self.chunks_count,), TriChunk)
		# logging.debug(f"{self.chunks_count} tri_chunks at {self.tri_chunks_address}")
		self.buffer_info.vert_chunks.seek(self.vert_chunks_address)
		self.vert_chunks = Array.from_stream(self.buffer_info.vert_chunks, self.context, 0, None, (self.chunks_count,), VertChunk)
		# logging.debug(f"{self.chunks_count} vert_chunks at {self.vert_chunks_address}")

	@property
	def tris(self, ):
		# if self.flag.flat_arrays:
		# print(self.tri_indices)
		# create non-overlapping tris from flattened tri indices
		tris_raw = np.reshape(self.tri_indices, (len(self.tri_indices) // 3, 3))
		# reverse each tri to account for the flipped normals from mirroring in blender
		return np.flip(tris_raw, axis=-1)
		# else:
		# 	return triangulate((self.tri_indices,))

	@tris.setter
	def tris(self, list_of_b_tris):
		# create chunks for each segment in tris
		self.tris_count = sum(len(tup[1]) for tup in list_of_b_tris)
		self.vert_chunks = Array(self.context, 0, None, (len(list_of_b_tris),), VertChunk,)
		self.tri_chunks = Array(self.context, 0, None, (len(list_of_b_tris),), TriChunk)
		for vert_chunk, tri_chunk, (b_bone_id, b_tris) in zip(self.vert_chunks, self.tri_chunks, list_of_b_tris):
			# logging.info(b_tris)
			# cast to uint16
			raw_tris = np.array(b_tris, dtype=np.uint8)
			# reverse tris
			raw_tris = np.flip(raw_tris, axis=-1)
			# flatten array
			tri_chunk.tri_indices = np.reshape(raw_tris, len(raw_tris) * 3)
			tri_chunk.tris_count = len(b_tris)
			tri_chunk.shell_index = self.shell_index
			tri_chunk.shell_count = self.shell_count
			# get the vertex count from the tri indices
			vert_chunk.vertex_count = np.max(tri_chunk.tri_indices) + 1
			vert_chunk.weights_flag.mesh_format = self.mesh_format
			if b_bone_id == -1:
				# dynamic weights, extra array
				vert_chunk.weights_flag.has_weights = True
			elif b_bone_id == -2:
				# no bone info, no weights
				vert_chunk.weights_flag.has_weights = False
				vert_chunk.weights_flag.bone_index = 0
			else:
				# static weights
				vert_chunk.weights_flag.has_weights = False
				vert_chunk.weights_flag.bone_index = b_bone_id
			vert_chunk.pack_base = self.pack_base
			# it is not a linear mapping apparently
			# JWE2 has these samples
			# [(8.0, 7.629452738910913e-06), (512.0, 0.0004885197849944234), (1024.0, 0.0009775171056389809), (2048.0, 0.001956947147846222), (4096.0, 0.003921568859368563)]
			vert_chunk.scale = self.get_scale(vert_chunk.pack_base)

	@staticmethod
	def get_scale_regressed(p):
		# a quadratic regression got close to 1.0 determination
		return 1.2285932501219967e-9 + 9.536674737032024e-7 * p + 9.14657200199282e-13 * math.pow(p, 2)

	@staticmethod
	def get_scale(pack_base):
		# scale is close to pack_base / PACKEDVEC_MAX but with some error
		# the error follows a predictable pattern according to the size of pack base
		base_exp = math.log2(pack_base)
		error = 4 ** (base_exp-10.0)
		return (error + pack_base) / PACKEDVEC_MAX

	def pack_verts(self):
		"""Repack flat lists into verts_data"""
		# prepare data in whole mesh array for assignment
		pack_swizzle_vectorized(self.vertices)
		pack_swizzle_vectorized(self.shapekeys)
		pack_swizzle_vectorized(self.normals)
		pack_swizzle_vectorized(self.tangents)
		vec3_to_oct(self.normals)
		vec3_to_oct(self.tangents)
		pack_ubyte_color(self.colors)
		offs = 0
		for vert_chunk, tri_chunk in zip(self.vert_chunks, self.tri_chunks):
			# (re)generate views into mesh vertex arrays for vert_chunk according to tri_chunk
			v_slice = np.s_[offs: offs + vert_chunk.vertex_count]
			self.init_vert_chunk_arrays(v_slice, vert_chunk)
			offs += vert_chunk.vertex_count
			# we have the views, so set bounds for the chunk (after swizzling)
			tri_chunk.bounds_min.set(np.min(vert_chunk.vertices, axis=0))
			tri_chunk.bounds_max.set(np.max(vert_chunk.vertices, axis=0))
			# for alpha blended shells
			if self.flag == 13:
				# set the loc value as center of gravity, or center of bounds?
				tri_chunk.loc.set(np.mean(vert_chunk.vertices, axis=0))
				# rot is probably related to the normals of the chunk

			# pack the verts
			if vert_chunk.weights_flag.mesh_format in (MeshFormat.SEPARATE, MeshFormat.UNK_FMT):
				scale_pack_vectorized(vert_chunk.vertices, vert_chunk.pack_base)
				pack_int64_vector(vert_chunk.packed_verts, vert_chunk.vertices.astype(np.int64), vert_chunk.negate_bitangents)
				if vert_chunk.weights_flag.has_weights:
					for vert, weight in zip(vert_chunk.weights, self.weights[v_slice]):
						vert["bone ids"], vert["bone weights"] = self.unpack_weights_list(weight)
			elif vert_chunk.weights_flag.mesh_format in (MeshFormat.INTERLEAVED_32, MeshFormat.INTERLEAVED_48):
				vert_chunk.meta["pos"] = vert_chunk.vertices
				vert_chunk.weights_flag.has_weights = False
			else:
				raise AttributeError(f"Unsupported mesh_format {self.mesh_format}")
			# store chunk's meta data
			if vert_chunk.weights_flag.mesh_format == MeshFormat.INTERLEAVED_32:
				vert_chunk.meta["shapekey"] = vert_chunk.shapekeys
				vert_chunk.meta["floats"] = vert_chunk.floats
			# currently, known uses of Interleaved48 use impostor uv atlas
			if vert_chunk.weights_flag.mesh_format == MeshFormat.INTERLEAVED_48:
				pack_ushort_vector_impostor(vert_chunk.uvs)
			else:
				pack_ushort_vector(vert_chunk.uvs)
			# assign the right views from the main arrays back to the chunks
			# print("bef", vert_chunk.meta)
			vert_chunk.meta["uvs"] = vert_chunk.uvs
			vert_chunk.meta["colors"] = vert_chunk.colors
			vert_chunk.meta["normal_oct"] = vert_chunk.normals[:, :2]
			vert_chunk.meta["tangent_oct"] = vert_chunk.tangents[:, :2]
			# print("after", vert_chunk.meta)

	def write_data(self):
		# save tris and verts per chunk, and update the offsets each time
		# write to the buffer_info that has been assigned to mesh
		self.vertex_count = len(self.vertices)
		# this may not be needed, but for now is used in update_buffer_2_bytes
		self.tri_index_count = len(self.tri_indices)
		for vert_chunk, tri_chunk in zip(self.vert_chunks, self.tri_chunks):
			# write vertices
			vert_chunk.vertex_offset = self.buffer_info.verts.tell()
			vert_chunk.vertex_count = len(vert_chunk.meta)
			# write the arrays if they exist, in this order
			if vert_chunk.weights_flag.mesh_format in (MeshFormat.SEPARATE, MeshFormat.UNK_FMT):
				self.buffer_info.verts.write(vert_chunk.packed_verts.tobytes())
				if vert_chunk.weights_flag.has_weights:
					if self.context.version >= 52:
						vert_chunk.packed_weights = np.zeros(dtype=np.uint64, shape=vert_chunk.vertex_count)
						pack_int64_weights(vert_chunk.packed_weights, vert_chunk.weights)
						self.buffer_info.verts.write(vert_chunk.packed_weights.tobytes())
					else:
						self.buffer_info.verts.write(vert_chunk.weights.tobytes())
			self.buffer_info.verts.write(vert_chunk.meta.tobytes())

			tri_chunk.tris_offset = self.buffer_info.tris.tell()
			# get tri indices of this chunk
			_tri_chunk_tri_indices = np.copy(tri_chunk.tri_indices)
			_tri_chunk_tri_indices -= np.min(_tri_chunk_tri_indices)
			tri_bytes = _tri_chunk_tri_indices.astype(np.uint8).tobytes()
			# extend tri array according to shell count
			# logging.debug(f"Writing {self.shell_count} shells of {len(self.tri_indices)} triangles")
			# for shell in range(self.shell_count):
			self.buffer_info.tris.write(tri_bytes)

		# write the chunks
		self.chunks_offset = self.buffer_info.tri_chunks.tell() // 64
		self.chunks_count = len(self.tri_chunks)
		Array.to_stream(self.tri_chunks, self.buffer_info.tri_chunks, self.context, dtype=TriChunk)
		Array.to_stream(self.vert_chunks, self.buffer_info.vert_chunks, self.context, dtype=VertChunk)

