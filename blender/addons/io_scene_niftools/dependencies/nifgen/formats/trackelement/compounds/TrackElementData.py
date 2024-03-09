from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackelement.imports import name_type_map


class TrackElementData(MemStruct):

	"""
	PC: 80 PZ: 48
	"""

	__name__ = 'TrackElementData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_0 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_2 = name_type_map['Uint'](self.context, 0, None)
		self.unk_3 = name_type_map['Ushort'].from_value(0)
		self.unk_4 = name_type_map['Ushort'].from_value(32)
		self.unk_5 = name_type_map['Uint'].from_value(1024)
		self.unk_6 = name_type_map['Uint'].from_value(1)
		self.unk_7 = name_type_map['Uint'].from_value(1)

		# 8 bytes when count is 1
		self.pad = name_type_map['Uint64'](self.context, 0, None)
		self.loop_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.ovl_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.catwalk = name_type_map['Pointer'](self.context, 0, name_type_map['TrackElementSub'])
		self.optional_catwalk = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'loop_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'ovl_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'catwalk', name_type_map['Pointer'], (0, name_type_map['TrackElementSub']), (False, None), (lambda context: context.version <= 18, None)
		yield 'unk_0', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'optional_catwalk', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_3', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'unk_4', name_type_map['Ushort'], (0, None), (False, 32), (None, None)
		yield 'unk_5', name_type_map['Uint'], (0, None), (False, 1024), (lambda context: context.version <= 18, None)
		yield 'unk_6', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'unk_7', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'pad', name_type_map['Uint64'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'loop_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'ovl_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		if instance.context.version <= 18:
			yield 'catwalk', name_type_map['Pointer'], (0, name_type_map['TrackElementSub']), (False, None)
			yield 'unk_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'optional_catwalk', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		if instance.context.version <= 18:
			yield 'unk_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_3', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'unk_4', name_type_map['Ushort'], (0, None), (False, 32)
		if instance.context.version <= 18:
			yield 'unk_5', name_type_map['Uint'], (0, None), (False, 1024)
		yield 'unk_6', name_type_map['Uint'], (0, None), (False, 1)
		yield 'unk_7', name_type_map['Uint'], (0, None), (False, 1)
		if instance.arg < 2:
			yield 'pad', name_type_map['Uint64'], (0, None), (False, None)
