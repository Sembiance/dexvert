from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class Pillar(MemStruct):

	__name__ = 'Pillar'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_int = name_type_map['Uint64'](self.context, 0, None)
		self.unk_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.unk_int_2 = name_type_map['Uint64'](self.context, 0, None)
		self.pillar_model = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.cap_model = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pillar_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'cap_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_int', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None), (None, None)
		yield 'unk_int_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pillar_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'cap_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_int', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_floats', Array, (0, None, (2,), name_type_map['Float']), (False, None)
		yield 'unk_int_2', name_type_map['Uint64'], (0, None), (False, None)
