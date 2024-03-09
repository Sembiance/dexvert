from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class BufferInfo(BaseStruct):

	"""
	Fragment data describing a MS2 buffer giving the size of the whole vertex and tri buffer.
	ZTUAC, DLA: 64 bytes verts, tris, uvs (incl. verts sometimes)
	PC: 32 bytes, lumps all data (pos, uv, weights, tris) into verts_size
	JWE: 48 bytes
	PZ old: 32 bytes?
	PZ1.6+ and JWE2: 56 bytes
	JWE2 Biosyn: 88 bytes, with 4 values, order of arrays in buffer is verts, tris, tri_chunks, vert_chunks
	
	JWE and PC, 16 bytes of 00 padding
	"""

	__name__ = 'BufferInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u_0 = name_type_map['Uint64'](self.context, 0, None)
		self.u_1 = name_type_map['Uint64'](self.context, 0, None)
		self.tri_chunks_size = name_type_map['Uint64'](self.context, 0, None)
		self.tri_chunks_ptr = name_type_map['Uint64'](self.context, 0, None)
		self.vert_chunks_size = name_type_map['Uint64'](self.context, 0, None)
		self.vert_chunks_ptr = name_type_map['Uint64'](self.context, 0, None)
		self.verts_size = name_type_map['Uint64'](self.context, 0, None)
		self.verts_ptr = name_type_map['Uint64'](self.context, 0, None)
		self.u_3 = name_type_map['Uint64'](self.context, 0, None)
		self.tris_size = name_type_map['Uint64'](self.context, 0, None)
		self.tris_ptr = name_type_map['Uint64'](self.context, 0, None)
		self.u_5 = name_type_map['Uint64'](self.context, 0, None)
		self.u_6 = name_type_map['Uint64'](self.context, 0, None)
		self.u_5 = name_type_map['Uint64'](self.context, 0, None)

		# from start of tris buffer
		self.uvs_size = name_type_map['Uint64'](self.context, 0, None)
		self.u_6 = name_type_map['Uint64'](self.context, 0, None)
		self.u_7 = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'u_0', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 32 <= context.version <= 47, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 32 <= context.version <= 47, None)
		yield 'tri_chunks_size', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 52, None)
		yield 'tri_chunks_ptr', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 52, None)
		yield 'vert_chunks_size', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 52, None)
		yield 'vert_chunks_ptr', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 52, None)
		yield 'verts_size', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'verts_ptr', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_3', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 48 <= context.version <= 52, None)
		yield 'tris_size', name_type_map['Uint64'], (0, None), (False, None), (lambda context: not (context.version == 32), None)
		yield 'tris_ptr', name_type_map['Uint64'], (0, None), (False, None), (lambda context: not (context.version == 32), None)
		yield 'u_5', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 48 <= context.version <= 52, None)
		yield 'u_6', name_type_map['Uint64'], (0, None), (False, None), (lambda context: 48 <= context.version <= 52, None)
		yield 'u_5', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'uvs_size', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'u_6', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'u_7', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 13, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 32 <= instance.context.version <= 47:
			yield 'u_0', name_type_map['Uint64'], (0, None), (False, None)
			yield 'u_1', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version >= 52:
			yield 'tri_chunks_size', name_type_map['Uint64'], (0, None), (False, None)
			yield 'tri_chunks_ptr', name_type_map['Uint64'], (0, None), (False, None)
			yield 'vert_chunks_size', name_type_map['Uint64'], (0, None), (False, None)
			yield 'vert_chunks_ptr', name_type_map['Uint64'], (0, None), (False, None)
		yield 'verts_size', name_type_map['Uint64'], (0, None), (False, None)
		yield 'verts_ptr', name_type_map['Uint64'], (0, None), (False, None)
		if 48 <= instance.context.version <= 52:
			yield 'u_3', name_type_map['Uint64'], (0, None), (False, None)
		if not (instance.context.version == 32):
			yield 'tris_size', name_type_map['Uint64'], (0, None), (False, None)
			yield 'tris_ptr', name_type_map['Uint64'], (0, None), (False, None)
		if 48 <= instance.context.version <= 52:
			yield 'u_5', name_type_map['Uint64'], (0, None), (False, None)
			yield 'u_6', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version <= 13:
			yield 'u_5', name_type_map['Uint64'], (0, None), (False, None)
			yield 'uvs_size', name_type_map['Uint64'], (0, None), (False, None)
			yield 'u_6', name_type_map['Uint64'], (0, None), (False, None)
			yield 'u_7', name_type_map['Uint64'], (0, None), (False, None)
