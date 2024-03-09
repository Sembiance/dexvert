from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackmesh.imports import name_type_map


class OffsetData(MemStruct):

	"""
	PC: 64 bytes
	"""

	__name__ = 'OffsetData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.z_0 = name_type_map['Uint64'](self.context, 0, None)
		self.z_1 = name_type_map['Uint64'](self.context, 0, None)
		self.relative_offset = name_type_map['Vector3'](self.context, 0, None)
		self.spacing = name_type_map['Float'](self.context, 0, None)
		self.one = name_type_map['Uint'](self.context, 0, None)
		self.z_2 = name_type_map['Uint'](self.context, 0, None)
		self.z_3 = name_type_map['Uint'](self.context, 0, None)
		self.count = name_type_map['Uint'](self.context, 0, None)
		self.z_4 = name_type_map['Uint'](self.context, 0, None)
		self.z_5 = name_type_map['Uint'](self.context, 0, None)
		self.offset_id = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'offset_id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'z_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'z_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'relative_offset', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'spacing', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'one', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'z_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'z_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'z_4', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'z_5', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'offset_id', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'z_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'z_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'relative_offset', name_type_map['Vector3'], (0, None), (False, None)
		yield 'spacing', name_type_map['Float'], (0, None), (False, None)
		yield 'one', name_type_map['Uint'], (0, None), (False, None)
		yield 'z_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'z_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'count', name_type_map['Uint'], (0, None), (False, None)
		yield 'z_4', name_type_map['Uint'], (0, None), (False, None)
		yield 'z_5', name_type_map['Uint'], (0, None), (False, None)
