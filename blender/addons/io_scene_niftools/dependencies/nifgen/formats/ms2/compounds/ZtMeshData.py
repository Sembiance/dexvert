import logging
import math
import numpy as np

from nifgen.formats.ms2.compounds.ZtTriBlockInfo import ZtTriBlockInfo
from nifgen.formats.ms2.compounds.ZtVertBlockInfo import ZtVertBlockInfo
from nifgen.formats.ms2.compounds.packing_utils import *
from plugin.utils.tristrip import triangulate
from nifgen.formats.ms2.compounds.MeshData import MeshData
from nifgen.formats.ms2.imports import name_type_map


class ZtMeshData(MeshData):

	"""
	64 bytes total, same layout for DLA and ZTUAC
	"""

	__name__ = 'ZtMeshData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# repeat
		self.tri_index_count = name_type_map['Uint'](self.context, 0, None)
		self.vertex_count = name_type_map['Uint'](self.context, 0, None)

		# stores count, -1 as ints
		self.tri_info_offset = name_type_map['Uint'](self.context, 0, None)

		# stores count, -1 as ints
		self.vert_info_offset = name_type_map['Uint'](self.context, 0, None)
		self.known_ff_0 = name_type_map['Int'](self.context, 0, None)
		self.tri_offset = name_type_map['Uint'](self.context, 0, None)

		# variable dtype, can include vertices too
		self.uv_offset = name_type_map['Uint'](self.context, 0, None)

		# if present, blocks of 24 bytes
		self.vertex_offset = name_type_map['Uint'](self.context, 0, None)
		self.unk_index = name_type_map['Short'](self.context, 0, None)
		self.one_0 = name_type_map['Ushort'](self.context, 0, None)

		# ?
		self.one_1 = name_type_map['Ushort'](self.context, 0, None)
		self.poweroftwo = name_type_map['Ushort'](self.context, 0, None)

		# bitfield
		self.flag = name_type_map['ModelFlagZT'](self.context, 0, None)

		# always zero
		self.zero_uac = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'tri_index_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tri_info_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vert_info_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'known_ff_0', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'tri_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'uv_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertex_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_index', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'one_0', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'one_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'poweroftwo', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'flag', name_type_map['ModelFlagDLA'], (0, None), (False, None), (lambda context: context.version <= 7, None)
		yield 'flag', name_type_map['ModelFlagZT'], (0, None), (False, None), (lambda context: context.version >= 13, None)
		yield 'zero_uac', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'tri_index_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'tri_info_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'vert_info_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'known_ff_0', name_type_map['Int'], (0, None), (False, None)
		yield 'tri_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'uv_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertex_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_index', name_type_map['Short'], (0, None), (False, None)
		yield 'one_0', name_type_map['Ushort'], (0, None), (False, None)
		yield 'one_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'poweroftwo', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 7:
			yield 'flag', name_type_map['ModelFlagDLA'], (0, None), (False, None)
		if instance.context.version >= 13:
			yield 'flag', name_type_map['ModelFlagZT'], (0, None), (False, None)
		yield 'zero_uac', name_type_map['Uint'], (0, None), (False, None)

	def init_arrays(self):
		self.vertices = np.empty((self.vertex_count, 3), np.float32)
		self.normals = np.empty((self.vertex_count, 3), np.float32)
		self.tangents = np.empty((self.vertex_count, 3), np.float32)
		try:
			uv_shape = self.dt_colors["uvs"].shape
			self.uvs = np.empty((self.vertex_count, *uv_shape), np.float32)
		except:
			self.uvs = None
		try:
			colors_shape = self.dt_colors["colors"].shape
			self.colors = np.empty((self.vertex_count, *colors_shape), np.float32)
		except:
			self.colors = None
		self.weights_info = {}

	def update_dtype(self):
		"""Update MeshData.dt (numpy dtype) according to MeshData.flag"""
		# basic shared stuff
		dt = [
			("bone ids", np.ubyte, (4,)),
			("bone weights", np.ubyte, (4,)),
			("pos", np.float16, (3,)),
			("one", np.float16),
			("normal", np.ubyte, (3,)),
			("winding", np.ubyte, ),  # not tested
			("tangent", np.ubyte, (3,)),
			("bone index", np.ubyte, ),  # not tested
		]
		size = self.guess_size(self.buffer_info.uvs_offsets, self.uv_offset, self.vertex_count)
		logging.info(f"Guessed size {size}")
		if 4294967295 == self.vertex_offset:
			if size == 24:
				# 24 bytes per vert, flag is unk
				dt_colors = [
					("pos", np.float16, (3,)),
					("one", np.float16),
					("normal", np.ubyte, (3,)),
					("winding", np.ubyte, ),  # not tested
					("tangent", np.ubyte, (3,)),
					("bone index", np.ubyte, ),  # not tested
					("colors", np.ubyte, (1, 4)),
					("uvs", np.ushort, (1, 2)),
				]
			else:
				# 20 bytes per vert
				dt_colors = [
					("pos", np.float16, (3,)),
					("one", np.float16),
					("normal", np.ubyte, (3,)),
					("winding", np.ubyte, ),  # not tested
					("tangent", np.ubyte, (3,)),
					("bone index", np.ubyte, ),  # not tested
					("uvs", np.ushort, (1, 2)),
				]
		else:
			# hack for zt monitor
			if size == 4:
				dt_colors = [
					("uvs", np.ushort, (1, 2)),
				]
			else:
				dt_colors = [
					("colors", np.ubyte, (1, 4)),
					("uvs", np.ushort, (1 + self.some_index, 2)),
				]
		self.dt = np.dtype(dt)
		self.dt_colors = np.dtype(dt_colors)
		self.update_shell_count()

	def read_verts(self):
		self.update_dtype()
		self.init_arrays()
		logging.info(self)
		try:
			self.buffer_info.verts.seek(self.tri_info_offset)
			tri_info = ZtTriBlockInfo.from_stream(self.buffer_info.verts, self.context, 0, None)
			logging.info(tri_info)
		except:
			logging.exception(f"tri_info failed @ {self.tri_info_offset} in {self.buffer_info.path}")
		try:
			self.buffer_info.verts.seek(self.vert_info_offset)
			vert_info = ZtVertBlockInfo.from_stream(self.buffer_info.verts, self.context, 0, None)
			logging.info(vert_info)
		except:
			logging.exception(f"vert_info failed @ {self.vert_info_offset} in {self.buffer_info.path}")
		# read vertices of this mesh
		self.verts_data = np.empty(dtype=self.dt, shape=self.vertex_count)
		self.colors_data = np.empty(dtype=self.dt_colors, shape=self.vertex_count)
		self.buffer_info.uvs.seek(self.uv_offset)
		# logging.debug(f"UV at {self.buffer_info.uvs.tell()}")
		self.buffer_info.uvs.readinto(self.colors_data)
		if 4294967295 != self.vertex_offset:
			self.buffer_info.verts.seek(self.vertex_offset)
			# logging.debug(f"{self.vertex_count} VERTS at {self.buffer_info.verts.tell()}")
			self.buffer_info.verts.readinto(self.verts_data)
			self.normals[:] = self.verts_data["normal"]
			self.tangents[:] = self.verts_data["tangent"]
			self.vertices[:] = self.verts_data["pos"]

			# if "bone weights" in self.dt.fields:
			bone_weights = self.verts_data["bone weights"].astype(np.float32) / 255
			self.get_blended_weights(self.verts_data["bone ids"], bone_weights)
		else:
			self.normals[:] = self.colors_data["normal"]
			self.tangents[:] = self.colors_data["tangent"]
			self.vertices[:] = self.colors_data["pos"]

		# first cast to the float uvs array so unpacking doesn't use int division
		if self.colors is not None:
			# first cast to the float colors array so unpacking doesn't use int division
			self.colors[:] = self.colors_data["colors"]
			unpack_ubyte_color(self.colors)
		if self.uvs is not None:
			self.uvs[:] = self.colors_data["uvs"]
			self.uvs /= 2048
		unpack_ubyte_vector(self.normals)
		unpack_ubyte_vector(self.tangents)
		unpack_swizzle_vectorized(self.vertices)
		unpack_swizzle_vectorized_b(self.normals)
		unpack_swizzle_vectorized(self.tangents)
		# self.get_static_weights(self.verts_data["bone index"], self.use_blended_weights)


