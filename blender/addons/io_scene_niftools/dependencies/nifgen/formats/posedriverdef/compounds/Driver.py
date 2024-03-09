from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.posedriverdef.imports import name_type_map


class Driver(MemStruct):

	"""
	48 bytes
	"""

	__name__ = 'Driver'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.a = name_type_map['Ubyte'](self.context, 0, None)
		self.b = name_type_map['Ubyte'](self.context, 0, None)
		self.c = name_type_map['Ushort'](self.context, 0, None)
		self.d = name_type_map['Uint'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_2 = name_type_map['Uint64'](self.context, 0, None)
		self.joint_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.driven_joint_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.data = name_type_map['Pointer'](self.context, 0, name_type_map['Data'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'joint_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'a', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'd', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'driven_joint_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['Pointer'], (0, name_type_map['Data']), (False, None), (None, None)
		yield 'unk_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'joint_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'a', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'b', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'c', name_type_map['Ushort'], (0, None), (False, None)
		yield 'd', name_type_map['Uint'], (0, None), (False, None)
		yield 'driven_joint_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'data', name_type_map['Pointer'], (0, name_type_map['Data']), (False, None)
		yield 'unk_2', name_type_map['Uint64'], (0, None), (False, None)
