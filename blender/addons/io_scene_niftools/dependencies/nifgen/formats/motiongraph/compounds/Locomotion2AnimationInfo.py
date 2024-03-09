from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Locomotion2AnimationInfo(MemStruct):

	"""
	16 bytes
	"""

	__name__ = 'Locomotion2AnimationInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.phase_entry_window = name_type_map['Float'].from_value(1.5)
		self.priority = name_type_map['Ushort'](self.context, 0, None)
		self.anim_type = name_type_map['Ubyte'](self.context, 0, None)
		self._pad = name_type_map['Ubyte'](self.context, 0, None)
		self.anim_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'anim_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'phase_entry_window', name_type_map['Float'], (0, None), (False, 1.5), (None, None)
		yield 'priority', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'anim_type', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield '_pad', name_type_map['Ubyte'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'anim_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'phase_entry_window', name_type_map['Float'], (0, None), (False, 1.5)
		yield 'priority', name_type_map['Ushort'], (0, None), (False, None)
		yield 'anim_type', name_type_map['Ubyte'], (0, None), (False, None)
		yield '_pad', name_type_map['Ubyte'], (0, None), (False, None)
