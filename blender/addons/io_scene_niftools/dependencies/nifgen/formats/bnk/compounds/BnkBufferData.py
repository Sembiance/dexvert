from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class BnkBufferData(BaseStruct):

	"""
	Buffer data of bnk files
	"""

	__name__ = 'BnkBufferData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# data size of aux of type b, can be in bnk's buffer 1, and maybe also an external aux b file
		self.size_b = name_type_map['Uint64'](self.context, 0, None)

		# 1, guess
		self.external_aux_b_count = name_type_map['Uint'](self.context, 0, None)

		# 1 for PC, 2 for PZ, JWE, 6 for ZTUAC
		self.total_aux_count = name_type_map['Uint'](self.context, 0, None)

		# variable
		self.streams_count = name_type_map['Uint'](self.context, 0, None)

		# 0
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# variable
		self.zeros_per_buffer = Array(self.context, 0, None, (0,), name_type_map['Uint64'])

		# data
		self.streams = Array(self.context, 0, None, (0,), name_type_map['StreamInfo'])

		# data
		self.name = name_type_map['ZString'](self.context, 0, None)

		# ext format subtypes
		self.external_b_suffix = name_type_map['ZString'](self.context, 0, None)

		# ext format subtypes
		self.external_s_suffix = name_type_map['ZString'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'size_b', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'external_aux_b_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'total_aux_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'streams_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (7,), name_type_map['Uint']), (False, None), (None, None)
		yield 'zeros_per_buffer', Array, (0, None, (None, 2,), name_type_map['Uint64']), (False, None), (None, None)
		yield 'streams', Array, (0, None, (None,), name_type_map['StreamInfo']), (False, None), (None, None)
		yield 'name', name_type_map['ZString'], (0, None), (False, None), (None, None)
		yield 'external_b_suffix', name_type_map['ZString'], (0, None), (False, None), (None, True)
		yield 'external_s_suffix', name_type_map['ZString'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'size_b', name_type_map['Uint64'], (0, None), (False, None)
		yield 'external_aux_b_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'total_aux_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'streams_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'zeros', Array, (0, None, (7,), name_type_map['Uint']), (False, None)
		yield 'zeros_per_buffer', Array, (0, None, (instance.external_aux_b_count, 2,), name_type_map['Uint64']), (False, None)
		yield 'streams', Array, (0, None, (instance.streams_count,), name_type_map['StreamInfo']), (False, None)
		yield 'name', name_type_map['ZString'], (0, None), (False, None)
		if instance.external_aux_b_count:
			yield 'external_b_suffix', name_type_map['ZString'], (0, None), (False, None)
		if instance.streams_count:
			yield 'external_s_suffix', name_type_map['ZString'], (0, None), (False, None)
