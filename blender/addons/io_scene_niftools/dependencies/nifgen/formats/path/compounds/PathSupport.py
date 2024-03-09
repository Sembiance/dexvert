from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class PathSupport(MemStruct):

	__name__ = 'PathSupport'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.distance = name_type_map['Float'].from_value(10.0)
		self._unk_int_1 = name_type_map['Uint'](self.context, 0, None)
		self.support = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'support', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'distance', name_type_map['Float'], (0, None), (False, 10.0), (None, None)
		yield '_unk_int_1', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'support', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'distance', name_type_map['Float'], (0, None), (False, 10.0)
		yield '_unk_int_1', name_type_map['Uint'], (0, None), (False, None)
