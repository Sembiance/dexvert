from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.particleeffect.imports import name_type_map


class NextRow1(MemStruct):

	__name__ = 'nextRow1'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk = name_type_map['Uint64'](self.context, 0, None)
		self.maybe_hash = name_type_map['Uint'](self.context, 0, None)
		self.count = name_type_map['Ushort'](self.context, 0, None)
		self.count_repeat = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'maybe_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'count_repeat', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None)
		yield 'maybe_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'count_repeat', name_type_map['Ushort'], (0, None), (False, None)
