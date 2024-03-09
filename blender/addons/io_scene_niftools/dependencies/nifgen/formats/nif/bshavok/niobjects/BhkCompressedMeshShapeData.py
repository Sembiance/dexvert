from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkRefObject import BhkRefObject
from nifgen.formats.nif.imports import name_type_map


class BhkCompressedMeshShapeData(BhkRefObject):

	"""
	A compressed mesh shape for collision in Skyrim.
	"""

	__name__ = 'bhkCompressedMeshShapeData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of bits in the shape-key reserved for a triangle index
		self.bits_per_index = name_type_map['Uint'].from_value(17)

		# Number of bits in the shape-key reserved for a triangle index and its winding
		self.bits_per_w_index = name_type_map['Uint'].from_value(18)

		# Mask used to get the triangle index and winding from a shape-key/
		self.mask_w_index = name_type_map['Uint'].from_value(262143)

		# Mask used to get the triangle index from a shape-key.
		self.mask_index = name_type_map['Uint'].from_value(131071)

		# Quantization error.
		self.error = name_type_map['Float'].from_value(0.001)
		self.aabb = name_type_map['HkAabb'](self.context, 0, None)
		self.welding_type = name_type_map['HkWeldingType'].ANTICLOCKWISE
		self.material_type = name_type_map['BhkCMSMatType'].SINGLE_VALUE_PER_CHUNK
		self.num_materials_32 = name_type_map['Uint'](self.context, 0, None)

		# Unused.
		self.materials_32 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.num_materials_16 = name_type_map['Uint'](self.context, 0, None)

		# Unused.
		self.materials_16 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.num_materials_8 = name_type_map['Uint'](self.context, 0, None)

		# Unused.
		self.materials_8 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.num_materials = name_type_map['Uint'].from_value(1)

		# Materials used by Chunks. Chunks refer to this table by index.
		self.chunk_materials = Array(self.context, 0, None, (0,), name_type_map['BhkMeshMaterial'])

		# Number of hkpNamedMeshMaterial. Unused.
		self.num_named_materials = name_type_map['Uint'](self.context, 0, None)

		# Number of chunk transformations
		self.num_transforms = name_type_map['Uint'].from_value(1)

		# Transforms used by Chunks. Chunks refer to this table by index.
		self.chunk_transforms = Array(self.context, 0, None, (0,), name_type_map['BhkQsTransform'])
		self.num_big_verts = name_type_map['Uint'](self.context, 0, None)

		# Vertices paired with Big Tris (triangles that are too large for chunks)
		self.big_verts = Array(self.context, 0, None, (0,), name_type_map['Vector4'])
		self.num_big_tris = name_type_map['Uint'](self.context, 0, None)

		# Triangles that are too large to fit in a chunk.
		self.big_tris = Array(self.context, 0, None, (0,), name_type_map['BhkCMSBigTri'])
		self.num_chunks = name_type_map['Uint'].from_value(1)
		self.chunks = Array(self.context, 0, None, (0,), name_type_map['BhkCMSChunk'])

		# Number of hkpCompressedMeshShape::ConvexPiece. Unused.
		self.num_convex_piece_a = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bits_per_index', name_type_map['Uint'], (0, None), (False, 17), (None, None)
		yield 'bits_per_w_index', name_type_map['Uint'], (0, None), (False, 18), (None, None)
		yield 'mask_w_index', name_type_map['Uint'], (0, None), (False, 262143), (None, None)
		yield 'mask_index', name_type_map['Uint'], (0, None), (False, 131071), (None, None)
		yield 'error', name_type_map['Float'], (0, None), (False, 0.001), (None, None)
		yield 'aabb', name_type_map['HkAabb'], (0, None), (False, None), (None, None)
		yield 'welding_type', name_type_map['HkWeldingType'], (0, None), (False, name_type_map['HkWeldingType'].ANTICLOCKWISE), (None, None)
		yield 'material_type', name_type_map['BhkCMSMatType'], (0, None), (False, name_type_map['BhkCMSMatType'].SINGLE_VALUE_PER_CHUNK), (None, None)
		yield 'num_materials_32', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'materials_32', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'num_materials_16', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'materials_16', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'num_materials_8', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'materials_8', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'num_materials', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'chunk_materials', Array, (0, None, (None,), name_type_map['BhkMeshMaterial']), (False, None), (None, None)
		yield 'num_named_materials', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_transforms', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'chunk_transforms', Array, (0, None, (None,), name_type_map['BhkQsTransform']), (False, None), (None, None)
		yield 'num_big_verts', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'big_verts', Array, (0, None, (None,), name_type_map['Vector4']), (False, None), (None, None)
		yield 'num_big_tris', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'big_tris', Array, (0, None, (None,), name_type_map['BhkCMSBigTri']), (False, None), (None, None)
		yield 'num_chunks', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'chunks', Array, (0, None, (None,), name_type_map['BhkCMSChunk']), (False, None), (None, None)
		yield 'num_convex_piece_a', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bits_per_index', name_type_map['Uint'], (0, None), (False, 17)
		yield 'bits_per_w_index', name_type_map['Uint'], (0, None), (False, 18)
		yield 'mask_w_index', name_type_map['Uint'], (0, None), (False, 262143)
		yield 'mask_index', name_type_map['Uint'], (0, None), (False, 131071)
		yield 'error', name_type_map['Float'], (0, None), (False, 0.001)
		yield 'aabb', name_type_map['HkAabb'], (0, None), (False, None)
		yield 'welding_type', name_type_map['HkWeldingType'], (0, None), (False, name_type_map['HkWeldingType'].ANTICLOCKWISE)
		yield 'material_type', name_type_map['BhkCMSMatType'], (0, None), (False, name_type_map['BhkCMSMatType'].SINGLE_VALUE_PER_CHUNK)
		yield 'num_materials_32', name_type_map['Uint'], (0, None), (False, None)
		yield 'materials_32', Array, (0, None, (instance.num_materials_32,), name_type_map['Uint']), (False, None)
		yield 'num_materials_16', name_type_map['Uint'], (0, None), (False, None)
		yield 'materials_16', Array, (0, None, (instance.num_materials_16,), name_type_map['Uint']), (False, None)
		yield 'num_materials_8', name_type_map['Uint'], (0, None), (False, None)
		yield 'materials_8', Array, (0, None, (instance.num_materials_8,), name_type_map['Uint']), (False, None)
		yield 'num_materials', name_type_map['Uint'], (0, None), (False, 1)
		yield 'chunk_materials', Array, (0, None, (instance.num_materials,), name_type_map['BhkMeshMaterial']), (False, None)
		yield 'num_named_materials', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_transforms', name_type_map['Uint'], (0, None), (False, 1)
		yield 'chunk_transforms', Array, (0, None, (instance.num_transforms,), name_type_map['BhkQsTransform']), (False, None)
		yield 'num_big_verts', name_type_map['Uint'], (0, None), (False, None)
		yield 'big_verts', Array, (0, None, (instance.num_big_verts,), name_type_map['Vector4']), (False, None)
		yield 'num_big_tris', name_type_map['Uint'], (0, None), (False, None)
		yield 'big_tris', Array, (0, None, (instance.num_big_tris,), name_type_map['BhkCMSBigTri']), (False, None)
		yield 'num_chunks', name_type_map['Uint'], (0, None), (False, 1)
		yield 'chunks', Array, (0, None, (instance.num_chunks,), name_type_map['BhkCMSChunk']), (False, None)
		yield 'num_convex_piece_a', name_type_map['Uint'], (0, None), (False, None)
