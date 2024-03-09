from nifgen.formats.fmvdesc.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class FMVDescRoot(MemStruct):

	__name__ = 'FMVDescRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self._zero_01 = name_type_map['Uint64'](self.context, 0, None)
		self._zero_02 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_65 = name_type_map['Uint'](self.context, 0, None)
		self.speed = name_type_map['Float'](self.context, 0, None)
		self._zero_03 = name_type_map['Uint64'](self.context, 0, None)
		self._zero_04 = name_type_map['Uint64'](self.context, 0, None)
		self._zero_05 = name_type_map['Uint64'](self.context, 0, None)
		self._zero_06 = name_type_map['Uint64'](self.context, 0, None)
		self.asset_path = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'asset_path', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield '_zero_01', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield '_zero_02', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_65', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'speed', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield '_zero_03', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield '_zero_04', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield '_zero_05', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield '_zero_06', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'asset_path', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield '_zero_01', name_type_map['Uint64'], (0, None), (False, None)
		yield '_zero_02', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_65', name_type_map['Uint'], (0, None), (False, None)
		yield 'speed', name_type_map['Float'], (0, None), (False, None)
		yield '_zero_03', name_type_map['Uint64'], (0, None), (False, None)
		yield '_zero_04', name_type_map['Uint64'], (0, None), (False, None)
		yield '_zero_05', name_type_map['Uint64'], (0, None), (False, None)
		yield '_zero_06', name_type_map['Uint64'], (0, None), (False, None)
