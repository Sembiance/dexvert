from nifgen.utils.mathutils import float_to_int
import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiGeometryData(NiObject):

	"""
	Mesh data: vertices, vertex normals, etc.
	Bethesda 20.2.0.7 NIFs: NiParticlesData no longer inherits from NiGeometryData and inherits NiObject directly.
	"Num Vertices" is renamed to "BS Max Vertices" for Bethesda 20.2 because Vertices, Normals, Tangents, Colors, and UV arrays
	do not have length for NiPSysData regardless of "Num" or booleans.
	"""

	__name__ = 'NiGeometryData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Always zero.
		self.group_id = name_type_map['Int'](self.context, 0, None)

		# Number of vertices.
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)

		# Bethesda uses this for max number of particles in NiPSysData.
		self.bs_max_vertices = name_type_map['Ushort'](self.context, 0, None)

		# Used with NiCollision objects when OBB or TRI is set.
		self.keep_flags = name_type_map['Byte'](self.context, 0, None)
		self.compress_flags = name_type_map['Byte'](self.context, 0, None)

		# Is the vertex array present? (Always non-zero.)
		# 1 (default): vertices and texture coordinates are stored in floats.
		# 15 (compression): vertices and texture coordinates are stored in half floats (found in 20.3.1.1 Fantasy Frontier Online).
		self.has_vertices = name_type_map['Bool'].from_value(True)

		# The mesh vertices.
		self.vertices = Array(self.context, 0, None, (0,), name_type_map['HalfVector3'])
		self.data_flags = name_type_map['NiGeometryDataFlags'](self.context, 0, None)
		self.bs_data_flags = name_type_map['BSGeometryDataFlags'](self.context, 0, None)
		self.material_crc = name_type_map['Uint'](self.context, 0, None)

		# Do we have lighting normals? These are essential for proper lighting: if not present, the model will only be influenced by ambient light.
		# 1 (default): normals are stored in floats.
		# 6 (compression): normals are stored in ByteVector3 (found in 20.3.1.1 Fantasy Frontier Online).
		# 15 (compression): normals are stored in HalfVector3 (found in 20.3.1.2 Aura Kingdom).
		self.has_normals = name_type_map['Bool'](self.context, 0, None)

		# The lighting normals.
		self.normals = Array(self.context, 0, None, (0,), name_type_map['SbyteVector3'])

		# Tangent vectors.
		self.tangents = Array(self.context, 0, None, (0,), name_type_map['Vector3'])

		# Bitangent vectors.
		self.bitangents = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.has_div_2_floats = name_type_map['Bool'](self.context, 0, None)
		self.div_2_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)

		# Do we have vertex colors? These are usually used to fine-tune the lighting of the model.
		# 
		# Note: how vertex colors influence the model can be controlled by having a NiVertexColorProperty object as a property child of the root node. If this property object is not present, the vertex colors fine-tune lighting.
		# 
		# Note 2: set to either 0 or 0xFFFFFFFF for NifTexture compatibility.
		# 
		# Note 3:
		# 1 (default): vertex colors are stored in 4 floats.
		# 7 (compression): vertex colors are stored in 4 bytes (found in 20.3.1.1 Fantasy Frontier Online).
		# 15 (compression): vertex colors are stored in 4 half floats (found in 20.3.1.2 Aura Kingdom).
		self.has_vertex_colors = name_type_map['Bool'](self.context, 0, None)

		# The vertex colors.
		self.vertex_colors = Array(self.context, 0, None, (0,), name_type_map['ByteColor4'])

		# The lower 6 bits of this field represent the number of UV texture sets. The rest is unused.
		self.data_flags = name_type_map['NiGeometryDataFlags'](self.context, 0, None)

		# Do we have UV coordinates?
		# 
		# Note: for compatibility with NifTexture, set this value to either 0x00000000 or 0xFFFFFFFF.
		self.has_uv = name_type_map['Bool'](self.context, 0, None)

		# The UV texture coordinates. They follow the OpenGL standard: some programs may require you to flip the second coordinate.
		self.uv_sets = Array(self.context, 0, None, (0,), name_type_map['HalfTexCoord'])

		# Consistency Flags
		self.consistency_flags = name_type_map['ConsistencyType'].CT_MUTABLE
		self.additional_data = name_type_map['Ref'](self.context, 0, name_type_map['AbstractAdditionalGeometryData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'group_id', name_type_map['Int'], (0, None), (False, None), (lambda context: context.version >= 167837810, None)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, True)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version < 34, True)
		yield 'bs_max_vertices', name_type_map['Ushort'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version >= 34, True)
		yield 'keep_flags', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'compress_flags', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'has_vertices', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'vertices', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, True)
		yield 'vertices', Array, (0, None, (None,), name_type_map['HalfVector3']), (False, None), (lambda context: context.version >= 335741185, True)
		yield 'data_flags', name_type_map['NiGeometryDataFlags'], (0, None), (False, None), (lambda context: context.version >= 167772416 and not ((context.version == 335675399) and (context.bs_header.bs_version > 0)), None)
		yield 'bs_data_flags', name_type_map['BSGeometryDataFlags'], (0, None), (False, None), (lambda context: (context.version == 335675399) and (context.bs_header.bs_version > 0), None)
		yield 'material_crc', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'has_normals', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'normals', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, True)
		yield 'normals', Array, (0, None, (None,), name_type_map['HalfVector3']), (False, None), (lambda context: context.version >= 335741186, True)
		yield 'normals', Array, (0, None, (None,), name_type_map['SbyteVector3']), (False, None), (lambda context: context.version >= 335741185, True)
		yield 'tangents', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'bitangents', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'has_div_2_floats', name_type_map['Bool'], (0, None), (False, None), (lambda context: 335740937 <= context.version <= 335740937 and (context.user_version == 131072) or (context.user_version == 196608), None)
		yield 'div_2_floats', Array, (0, None, (None,), name_type_map['Float']), (False, None), (lambda context: 335740937 <= context.version <= 335740937 and (context.user_version == 131072) or (context.user_version == 196608), True)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, None)
		yield 'has_vertex_colors', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'vertex_colors', Array, (0, None, (None,), name_type_map['Color4']), (False, (1.0, 1.0, 1.0, 1.0)), (None, True)
		yield 'vertex_colors', Array, (0, None, (None,), name_type_map['HalfColor4']), (False, None), (lambda context: context.version >= 335741186, True)
		yield 'vertex_colors', Array, (0, None, (None,), name_type_map['ByteColor4']), (False, None), (lambda context: context.version >= 335741185, True)
		yield 'data_flags', name_type_map['NiGeometryDataFlags'], (0, None), (False, None), (lambda context: context.version <= 67240448, None)
		yield 'has_uv', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 67108866, None)
		yield 'uv_sets', Array, (0, None, (None, None,), name_type_map['TexCoord']), (False, None), (None, True)
		yield 'uv_sets', Array, (0, None, (None, None,), name_type_map['HalfTexCoord']), (False, None), (lambda context: context.version >= 335741185, True)
		yield 'consistency_flags', name_type_map['ConsistencyType'], (0, None), (False, name_type_map['ConsistencyType'].CT_MUTABLE), (lambda context: context.version >= 167772416, None)
		yield 'additional_data', name_type_map['Ref'], (0, name_type_map['AbstractAdditionalGeometryData']), (False, None), (lambda context: context.version >= 335544324, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837810:
			yield 'group_id', name_type_map['Int'], (0, None), (False, None)
		if not isinstance(instance, name_type_map['NiPSysData']):
			yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.bs_header.bs_version < 34 and isinstance(instance, name_type_map['NiPSysData']):
			yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version >= 34 and isinstance(instance, name_type_map['NiPSysData']):
			yield 'bs_max_vertices', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 167837696:
			yield 'keep_flags', name_type_map['Byte'], (0, None), (False, None)
			yield 'compress_flags', name_type_map['Byte'], (0, None), (False, None)
		yield 'has_vertices', name_type_map['Bool'], (0, None), (False, True)
		if (instance.has_vertices > 0) and (instance.has_vertices != 15):
			yield 'vertices', Array, (0, None, (instance.num_vertices,), name_type_map['Vector3']), (False, None)
		if instance.context.version >= 335741185 and instance.has_vertices == 15:
			yield 'vertices', Array, (0, None, (instance.num_vertices,), name_type_map['HalfVector3']), (False, None)
		if instance.context.version >= 167772416 and not ((instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0)):
			yield 'data_flags', name_type_map['NiGeometryDataFlags'], (0, None), (False, None)
		if (instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 0):
			yield 'bs_data_flags', name_type_map['BSGeometryDataFlags'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version > 34:
			yield 'material_crc', name_type_map['Uint'], (0, None), (False, None)
		yield 'has_normals', name_type_map['Bool'], (0, None), (False, None)
		if (instance.has_normals > 0) and ((instance.has_normals != 6) and (instance.has_normals != 15)):
			yield 'normals', Array, (0, None, (instance.num_vertices,), name_type_map['Vector3']), (False, None)
		if instance.context.version >= 335741186 and instance.has_normals == 15:
			yield 'normals', Array, (0, None, (instance.num_vertices,), name_type_map['HalfVector3']), (False, None)
		if instance.context.version >= 335741185 and instance.has_normals == 6:
			yield 'normals', Array, (0, None, (instance.num_vertices,), name_type_map['SbyteVector3']), (False, None)
		if instance.context.version >= 167837696 and instance.has_normals and (((instance.data_flags | instance.bs_data_flags) & 4096) != 0):
			yield 'tangents', Array, (0, None, (instance.num_vertices,), name_type_map['Vector3']), (False, None)
			yield 'bitangents', Array, (0, None, (instance.num_vertices,), name_type_map['Vector3']), (False, None)
		if 335740937 <= instance.context.version <= 335740937 and (instance.context.user_version == 131072) or (instance.context.user_version == 196608):
			yield 'has_div_2_floats', name_type_map['Bool'], (0, None), (False, None)
		if 335740937 <= instance.context.version <= 335740937 and (instance.context.user_version == 131072) or (instance.context.user_version == 196608) and instance.has_div_2_floats:
			yield 'div_2_floats', Array, (0, None, (instance.num_vertices,), name_type_map['Float']), (False, None)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		yield 'has_vertex_colors', name_type_map['Bool'], (0, None), (False, None)
		if (instance.has_vertex_colors > 0) and ((instance.has_vertex_colors != 7) and (instance.has_vertex_colors != 15)):
			yield 'vertex_colors', Array, (0, None, (instance.num_vertices,), name_type_map['Color4']), (False, (1.0, 1.0, 1.0, 1.0))
		if instance.context.version >= 335741186 and instance.has_vertex_colors == 15:
			yield 'vertex_colors', Array, (0, None, (instance.num_vertices,), name_type_map['HalfColor4']), (False, None)
		if instance.context.version >= 335741185 and instance.has_vertex_colors == 7:
			yield 'vertex_colors', Array, (0, None, (instance.num_vertices,), name_type_map['ByteColor4']), (False, None)
		if instance.context.version <= 67240448:
			yield 'data_flags', name_type_map['NiGeometryDataFlags'], (0, None), (False, None)
		if instance.context.version <= 67108866:
			yield 'has_uv', name_type_map['Bool'], (0, None), (False, None)
		if (instance.has_vertices > 0) and (instance.has_vertices != 15):
			yield 'uv_sets', Array, (0, None, ((instance.data_flags & 63) | (instance.bs_data_flags & 1), instance.num_vertices,), name_type_map['TexCoord']), (False, None)
		if instance.context.version >= 335741185 and instance.has_vertices == 15:
			yield 'uv_sets', Array, (0, None, ((instance.data_flags & 63) | (instance.bs_data_flags & 1), instance.num_vertices,), name_type_map['HalfTexCoord']), (False, None)
		if instance.context.version >= 167772416:
			yield 'consistency_flags', name_type_map['ConsistencyType'], (0, None), (False, name_type_map['ConsistencyType'].CT_MUTABLE)
		if instance.context.version >= 335544324:
			yield 'additional_data', name_type_map['Ref'], (0, name_type_map['AbstractAdditionalGeometryData']), (False, None)
	"""
	>>> from pyffi.formats.nif import NifFormat
	>>> geomdata = NifFormat.NiGeometryData()
	>>> geomdata.num_vertices = 3
	>>> geomdata.has_vertices = True
	>>> geomdata.has_normals = True
	>>> geomdata.has_vertex_colors = True
	>>> geomdata.num_uv_sets = 2
	>>> geomdata.vertices.update_size()
	>>> geomdata.normals.update_size()
	>>> geomdata.vertex_colors.update_size()
	>>> geomdata.uv_sets.update_size()
	>>> geomdata.vertices[0].x = 1
	>>> geomdata.vertices[0].y = 2
	>>> geomdata.vertices[0].z = 3
	>>> geomdata.vertices[1].x = 4
	>>> geomdata.vertices[1].y = 5
	>>> geomdata.vertices[1].z = 6
	>>> geomdata.vertices[2].x = 1.200001
	>>> geomdata.vertices[2].y = 3.400001
	>>> geomdata.vertices[2].z = 5.600001
	>>> geomdata.normals[0].x = 0
	>>> geomdata.normals[0].y = 0
	>>> geomdata.normals[0].z = 1
	>>> geomdata.normals[1].x = 0
	>>> geomdata.normals[1].y = 1
	>>> geomdata.normals[1].z = 0
	>>> geomdata.normals[2].x = 1
	>>> geomdata.normals[2].y = 0
	>>> geomdata.normals[2].z = 0
	>>> geomdata.vertex_colors[1].r = 0.310001
	>>> geomdata.vertex_colors[1].g = 0.320001
	>>> geomdata.vertex_colors[1].b = 0.330001
	>>> geomdata.vertex_colors[1].a = 0.340001
	>>> geomdata.uv_sets[0][0].u = 0.990001
	>>> geomdata.uv_sets[0][0].v = 0.980001
	>>> geomdata.uv_sets[0][2].u = 0.970001
	>>> geomdata.uv_sets[0][2].v = 0.960001
	>>> geomdata.uv_sets[1][0].v = 0.910001
	>>> geomdata.uv_sets[1][0].v = 0.920001
	>>> geomdata.uv_sets[1][2].v = 0.930001
	>>> geomdata.uv_sets[1][2].v = 0.940001
	>>> for h in geomdata.get_vertex_hash_generator():
	...	 print(h)
	(1000, 2000, 3000, 0, 0, 1000, 99000, 98000, 0, 92000, 0, 0, 0, 0)
	(4000, 5000, 6000, 0, 1000, 0, 0, 0, 0, 0, 310, 320, 330, 340)
	(1200, 3400, 5600, 1000, 0, 0, 97000, 96000, 0, 94000, 0, 0, 0, 0)
	"""
	def update_center_radius(self):
		"""Recalculate center and radius of the data."""
		# in case there are no vertices, set center and radius to zero
		if len(self.vertices) == 0:
			self.bounding_sphere.center.x = 0.0
			self.bounding_sphere.center.y = 0.0
			self.bounding_sphere.center.z = 0.0
			self.bounding_sphere.radius = 0.0
			return

		# find extreme values in x, y, and z direction
		lowx = min([v.x for v in self.vertices])
		lowy = min([v.y for v in self.vertices])
		lowz = min([v.z for v in self.vertices])
		highx = max([v.x for v in self.vertices])
		highy = max([v.y for v in self.vertices])
		highz = max([v.z for v in self.vertices])

		# center is in the center of the bounding box
		cx = (lowx + highx) * 0.5
		cy = (lowy + highy) * 0.5
		cz = (lowz + highz) * 0.5
		self.bounding_sphere.center.x = cx
		self.bounding_sphere.center.y = cy
		self.bounding_sphere.center.z = cz

		# radius is the largest distance from the center
		r2 = 0.0
		for v in self.vertices:
			dx = cx - v.x
			dy = cy - v.y
			dz = cz - v.z
			r2 = max(r2, dx*dx+dy*dy+dz*dz)
		self.bounding_sphere.radius = r2 ** 0.5

	def apply_scale(self, scale):
		"""Apply scale factor on data."""
		if abs(scale - 1.0) <= NifFormat.EPSILON: return
		super().apply_scale(scale)
		for v in self.vertices:
			v.x *= scale
			v.y *= scale
			v.z *= scale
		self.bounding_sphere.apply_scale(scale)

	def get_vertex_hash_generator(
		self,
		vertexprecision=3, normalprecision=3,
		uvprecision=5, vcolprecision=3):
		"""Generator which produces a tuple of integers for each
		(vertex, normal, uv, vcol), to ease detection of duplicate
		vertices. The precision parameters denote number of
		significant digits behind the comma.

		Default for uvprecision should really be high because for
		very large models the uv coordinates can be very close
		together.

		For vertexprecision, 3 seems usually enough (maybe we'll
		have to increase this at some point).

		:param vertexprecision: Precision to be used for vertices.
		:type vertexprecision: float
		:param normalprecision: Precision to be used for normals.
		:type normalprecision: float
		:param uvprecision: Precision to be used for uvs.
		:type uvprecision: float
		:param vcolprecision: Precision to be used for vertex colors.
		:type vcolprecision: float
		:return: A generator yielding a hash value for each vertex.
		"""
		
		verts = self.vertices if self.has_vertices else None
		norms = self.normals if self.has_normals else None
		uvsets = self.uv_sets if len(self.uv_sets) else None
		vcols = self.vertex_colors if self.has_vertex_colors else None
		vertexfactor = 10 ** vertexprecision
		normalfactor = 10 ** normalprecision
		uvfactor = 10 ** uvprecision
		vcolfactor = 10 ** vcolprecision
		for i in range(self.num_vertices):
			h = []
			if verts:
				h.extend([float_to_int(x * vertexfactor)
						 for x in [verts[i].x, verts[i].y, verts[i].z]])
			if norms:
				h.extend([float_to_int(x * normalfactor)
						  for x in [norms[i].x, norms[i].y, norms[i].z]])
			if uvsets:
				for uvset in uvsets:
					# uvs sometimes have NaN, for example:
					# oblivion/meshes/architecture/anvil/anvildooruc01.nif
					h.extend([float_to_int(x * uvfactor)
							  for x in [uvset[i].u, uvset[i].v]])
			if vcols:
				h.extend([float_to_int(x * vcolfactor)
						  for x in [vcols[i].r, vcols[i].g,
									vcols[i].b, vcols[i].a]])
			yield tuple(h)

