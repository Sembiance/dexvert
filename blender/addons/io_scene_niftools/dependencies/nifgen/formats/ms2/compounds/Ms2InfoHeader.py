from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class Ms2InfoHeader(BaseStruct):

	"""
	Custom header struct
	"""

	__name__ = 'Ms2InfoHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.biosyn = name_type_map['BiosynVersion'](self.context, 0, None)
		self.bone_info_size = name_type_map['Uint'](self.context, 0, None)
		self.num_streams = name_type_map['Uint'](self.context, 0, None)
		self.info = name_type_map['Ms2Root'](self.context, 0, None)

		# used since DLA
		self.buffer_pointers = Array(self.context, 0, None, (0,), name_type_map['BufferPresence'])
		self.mdl_2_names = Array(self.context, 0, None, (0,), name_type_map['ZString'])
		self.modelstream_names = Array(self.context, 0, None, (0,), name_type_map['ZString'])
		self.buffer_0 = name_type_map['Buffer0'](self.context, self.info, None)
		self.buffer_infos = Array(self.context, 0, None, (0,), name_type_map['BufferInfo'])
		self.model_infos = Array(self.context, 0, None, (0,), name_type_map['ModelInfo'])

		# handles interleaved (old) or separate (new) styles for models and bone infos
		self.models_reader = name_type_map['ModelReader'](self.context, self.model_infos, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'biosyn', name_type_map['BiosynVersion'], (0, None), (False, None), (None, None)
		yield 'bone_info_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_streams', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'info', name_type_map['Ms2Root'], (0, None), (False, None), (None, None)
		yield 'buffer_pointers', Array, (0, None, (None,), name_type_map['BufferPresence']), (False, None), (lambda context: context.version >= 7, None)
		yield 'mdl_2_names', Array, (0, None, (None,), name_type_map['ZString']), (False, None), (None, None)
		yield 'modelstream_names', Array, (0, None, (None,), name_type_map['ZString']), (False, None), (None, None)
		yield 'buffer_0', name_type_map['Buffer0'], (None, None), (False, None), (None, None)
		yield 'buffer_infos', Array, (0, None, (None,), name_type_map['BufferInfo']), (False, None), (None, None)
		yield 'model_infos', Array, (0, None, (None,), name_type_map['ModelInfo']), (False, None), (None, None)
		yield 'models_reader', name_type_map['ModelReader'], (None, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'biosyn', name_type_map['BiosynVersion'], (0, None), (False, None)
		yield 'bone_info_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_streams', name_type_map['Uint'], (0, None), (False, None)
		yield 'info', name_type_map['Ms2Root'], (0, None), (False, None)
		if instance.context.version >= 7:
			yield 'buffer_pointers', Array, (0, None, (instance.info.vertex_buffer_count,), name_type_map['BufferPresence']), (False, None)
		yield 'mdl_2_names', Array, (0, None, (instance.info.mdl_2_count,), name_type_map['ZString']), (False, None)
		yield 'modelstream_names', Array, (0, None, (instance.num_streams,), name_type_map['ZString']), (False, None)
		yield 'buffer_0', name_type_map['Buffer0'], (instance.info, None), (False, None)
		yield 'buffer_infos', Array, (0, None, (instance.info.vertex_buffer_count,), name_type_map['BufferInfo']), (False, None)
		yield 'model_infos', Array, (0, None, (instance.info.mdl_2_count,), name_type_map['ModelInfo']), (False, None)
		yield 'models_reader', name_type_map['ModelReader'], (instance.model_infos, None), (False, None)
