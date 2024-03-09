from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackelement.imports import name_type_map


class TrackElementSub(MemStruct):

	"""
	PC: 32
	"""

	__name__ = 'TrackElementSub'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_0 = name_type_map['Uint64'](self.context, 0, None)
		self.catwalk_right_lsm = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.catwalk_left_lsm = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.catwalk_both_lsm = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'catwalk_right_lsm', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'catwalk_left_lsm', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'catwalk_both_lsm', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'catwalk_right_lsm', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'catwalk_left_lsm', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'catwalk_both_lsm', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'unk_0', name_type_map['Uint64'], (0, None), (False, None)
