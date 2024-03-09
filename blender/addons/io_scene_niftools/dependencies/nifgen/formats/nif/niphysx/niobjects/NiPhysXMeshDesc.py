from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXMeshDesc(NiObject):

	"""
	Holds mesh data for streaming.
	"""

	__name__ = 'NiPhysXMeshDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.is_convex = name_type_map['Bool'](self.context, 0, None)
		self.mesh_name = name_type_map['NiFixedString'](self.context, 0, None)
		self.mesh_data = name_type_map['ByteArray'](self.context, 0, None)
		self.back_compat_vertex_map_size = name_type_map['Ushort'](self.context, 0, None)
		self.back_compat_vertex_map = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.mesh_flags = name_type_map['Uint'](self.context, 0, None)
		self.mesh_paging_mode = name_type_map['Uint'](self.context, 0, None)
		self.is_hardware = name_type_map['Bool'](self.context, 0, None)
		self.flags = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'is_convex', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 335740932, None)
		yield 'mesh_name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'mesh_data', name_type_map['ByteArray'], (0, None), (False, None), (None, None)
		yield 'back_compat_vertex_map_size', name_type_map['Ushort'], (0, None), (False, None), (lambda context: 335740933 <= context.version <= 503447554, None)
		yield 'back_compat_vertex_map', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (lambda context: 335740933 <= context.version <= 503447554, None)
		yield 'mesh_flags', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'mesh_paging_mode', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335740929, None)
		yield 'is_hardware', name_type_map['Bool'], (0, None), (False, None), (lambda context: 335740930 <= context.version <= 335740932, None)
		yield 'flags', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 335740933, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 335740932:
			yield 'is_convex', name_type_map['Bool'], (0, None), (False, None)
		yield 'mesh_name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'mesh_data', name_type_map['ByteArray'], (0, None), (False, None)
		if 335740933 <= instance.context.version <= 503447554:
			yield 'back_compat_vertex_map_size', name_type_map['Ushort'], (0, None), (False, None)
			yield 'back_compat_vertex_map', Array, (0, None, (instance.back_compat_vertex_map_size,), name_type_map['Ushort']), (False, None)
		yield 'mesh_flags', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335740929:
			yield 'mesh_paging_mode', name_type_map['Uint'], (0, None), (False, None)
		if 335740930 <= instance.context.version <= 335740932:
			yield 'is_hardware', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335740933:
			yield 'flags', name_type_map['Byte'], (0, None), (False, None)
