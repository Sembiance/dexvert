from nifgen.array import Array
from nifgen.formats.guestonrideanimsettings.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class GuestOnRideAnimSettingsChild(MemStruct):

	__name__ = 'GuestOnRideAnimSettingsChild'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bools = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		self.float_0 = name_type_map['Float'](self.context, 0, None)
		self.unk_0 = name_type_map['Uint'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_2 = name_type_map['Uint'](self.context, 0, None)
		self.unk_3 = name_type_map['Uint'](self.context, 0, None)
		self.unk_4 = name_type_map['Uint'](self.context, 0, None)
		self.unk_5 = name_type_map['Uint'](self.context, 0, None)
		self.str_0 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.str_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.str_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.str_3 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.str_4 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.str_5 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.str_6 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'str_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'str_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'str_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'str_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'str_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'str_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'str_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'bools', Array, (0, None, (60,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'float_0', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_4', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_5', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'str_0', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'str_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'str_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'str_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'str_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'str_5', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'str_6', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'bools', Array, (0, None, (60,), name_type_map['Ubyte']), (False, None)
		yield 'float_0', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_4', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_5', name_type_map['Uint'], (0, None), (False, None)
