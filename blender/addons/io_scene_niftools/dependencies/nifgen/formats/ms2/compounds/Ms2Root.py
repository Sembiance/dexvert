from nifgen.array import Array
from nifgen.formats.ms2.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Ms2Root(MemStruct):

	"""
	root header of the ms2
	48 bytes
	"""

	__name__ = 'Ms2Root'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# see version tag
		self.version = name_type_map['MainVersion'](self.context, 0, None)

		# total count of vertex buffers, including streamed buffers
		self.vertex_buffer_count = name_type_map['Ushort'](self.context, 0, None)
		self.mdl_2_count = name_type_map['Ushort'](self.context, 0, None)

		# count of names in ms2 buffer0
		self.name_count = name_type_map['Ushort'](self.context, 0, None)

		# -1 if there is no vertex buffer at all; else index of static buffers in total buffers
		self.static_buffer_index = name_type_map['Short'](self.context, 0, None)
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# ms2's static buffer_info or empty (if no buffers)
		self.buffer_infos = name_type_map['ArrayPointer'](self.context, self.vertex_buffer_count, name_type_map['BufferInfo'])

		# one for each mdl2
		self.model_infos = name_type_map['ArrayPointer'](self.context, self.mdl_2_count, name_type_map['ModelInfo'])

		# links buffers to ms2 dependencies if they are streamed
		self.buffer_pointers = name_type_map['ArrayPointer'](self.context, self.vertex_buffer_count, name_type_map['BufferPresence'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'version', name_type_map['MainVersion'], (0, None), (False, None), (None, None)
		yield 'vertex_buffer_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'mdl_2_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'name_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'static_buffer_index', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (None, None)
		yield 'buffer_infos', name_type_map['ArrayPointer'], (None, name_type_map['BufferInfo']), (False, None), (None, None)
		yield 'model_infos', name_type_map['ArrayPointer'], (None, name_type_map['ModelInfo']), (False, None), (None, None)
		yield 'buffer_pointers', name_type_map['ArrayPointer'], (None, name_type_map['BufferPresence']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'version', name_type_map['MainVersion'], (0, None), (False, None)
		yield 'vertex_buffer_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'mdl_2_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'name_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'static_buffer_index', name_type_map['Short'], (0, None), (False, None)
		yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, None)
		yield 'buffer_infos', name_type_map['ArrayPointer'], (instance.vertex_buffer_count, name_type_map['BufferInfo']), (False, None)
		yield 'model_infos', name_type_map['ArrayPointer'], (instance.mdl_2_count, name_type_map['ModelInfo']), (False, None)
		yield 'buffer_pointers', name_type_map['ArrayPointer'], (instance.vertex_buffer_count, name_type_map['BufferPresence']), (False, None)
