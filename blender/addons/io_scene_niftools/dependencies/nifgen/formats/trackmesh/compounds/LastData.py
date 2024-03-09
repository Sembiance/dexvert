from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackmesh.imports import name_type_map


class LastData(MemStruct):

	"""
	PC: 120 bytes
	"""

	__name__ = 'LastData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.p_1_count = name_type_map['Uint64'](self.context, 0, None)
		self.b = name_type_map['Uint64'](self.context, 0, None)
		self.c = name_type_map['Uint64'](self.context, 0, None)
		self.p_2_count = name_type_map['Uint64'](self.context, 0, None)
		self.p_3_count = name_type_map['Uint64'](self.context, 0, None)
		self.f = name_type_map['Uint64'](self.context, 0, None)
		self.g = name_type_map['Uint64'](self.context, 0, None)
		self.p_4_count = name_type_map['Uint64'](self.context, 0, None)
		self.p_5_count = name_type_map['Uint64'](self.context, 0, None)
		self.some_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.p_1 = name_type_map['Pointer'](self.context, 0, None)
		self.p_2 = name_type_map['Pointer'](self.context, 0, None)
		self.p_3 = name_type_map['Pointer'](self.context, 0, None)
		self.p_4 = name_type_map['Pointer'](self.context, 0, None)
		self.p_5 = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'some_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'p_1', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'p_1_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'p_2', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'p_2_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'p_3', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'p_3_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'f', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'g', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'p_4', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'p_4_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'p_5', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'p_5_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'some_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'p_1', name_type_map['Pointer'], (0, None), (False, None)
		yield 'p_1_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'b', name_type_map['Uint64'], (0, None), (False, None)
		yield 'c', name_type_map['Uint64'], (0, None), (False, None)
		yield 'p_2', name_type_map['Pointer'], (0, None), (False, None)
		yield 'p_2_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'p_3', name_type_map['Pointer'], (0, None), (False, None)
		yield 'p_3_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'f', name_type_map['Uint64'], (0, None), (False, None)
		yield 'g', name_type_map['Uint64'], (0, None), (False, None)
		yield 'p_4', name_type_map['Pointer'], (0, None), (False, None)
		yield 'p_4_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'p_5', name_type_map['Pointer'], (0, None), (False, None)
		yield 'p_5_count', name_type_map['Uint64'], (0, None), (False, None)
