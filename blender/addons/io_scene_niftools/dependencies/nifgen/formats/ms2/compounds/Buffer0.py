from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class Buffer0(BaseStruct):

	__name__ = 'Buffer0'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# djb2 hashes
		self.name_hashes = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# names
		self.names = Array(self.context, 0, None, (0,), name_type_map['ZString'])

		# align to 4
		self.names_padding = name_type_map['PadAlign'](self.context, 4, self.names)
		self.zt_streams_header = name_type_map['StreamsZTHeader'](self.context, self.arg, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name_hashes', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'names', Array, (0, None, (None,), name_type_map['ZString']), (False, None), (None, None)
		yield 'names_padding', name_type_map['PadAlign'], (4, None), (False, None), (lambda context: context.version >= 50, None)
		yield 'zt_streams_header', name_type_map['StreamsZTHeader'], (None, None), (False, None), (lambda context: context.version <= 13, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name_hashes', Array, (0, None, (instance.arg.name_count,), name_type_map['Uint']), (False, None)
		yield 'names', Array, (0, None, (instance.arg.name_count,), name_type_map['ZString']), (False, None)
		if instance.context.version >= 50:
			yield 'names_padding', name_type_map['PadAlign'], (4, instance.names), (False, None)
		if instance.context.version <= 13:
			yield 'zt_streams_header', name_type_map['StreamsZTHeader'], (instance.arg, None), (False, None)
