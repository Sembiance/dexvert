from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.wmeta.imports import name_type_map


class EventEntry(MemStruct):

	"""
	PC: 56 bytes
	JWE2: 40 bytes
	# todo - improve versioning
	"""

	__name__ = 'EventEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.hash = name_type_map['Uint'](self.context, 0, None)
		self.zero = name_type_map['Uint'](self.context, 0, None)
		self.zero_2 = name_type_map['Ushort'](self.context, 0, None)
		self.size = name_type_map['Ushort'](self.context, 0, None)
		self.flag_0 = name_type_map['Uint'](self.context, 0, None)
		self.flag_1 = name_type_map['Uint'](self.context, 0, None)
		self.flag_2 = name_type_map['Uint'](self.context, 0, None)
		self.zero_3 = name_type_map['Uint64'](self.context, 0, None)
		self.flag_3 = name_type_map['Uint'](self.context, 0, None)
		self.hash_b = name_type_map['Uint'](self.context, 0, None)
		self.hash_c = name_type_map['Uint'](self.context, 0, None)
		self.zero_4 = name_type_map['Uint'](self.context, 0, None)
		self.u_2 = name_type_map['Uint'](self.context, 0, None)
		self.u_1 = name_type_map['Uint'](self.context, 0, None)
		self.block_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'block_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (lambda context: context.version <= 18, None)
		yield 'zero_2', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'size', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'flag_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'flag_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'flag_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_3', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'flag_3', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'hash_b', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'hash_c', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_4', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'u_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 19, None)
		yield 'u_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 19, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 18:
			yield 'block_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
			yield 'zero_2', name_type_map['Ushort'], (0, None), (False, None)
			yield 'size', name_type_map['Ushort'], (0, None), (False, None)
		yield 'flag_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'flag_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'flag_2', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 18:
			yield 'zero_3', name_type_map['Uint64'], (0, None), (False, None)
			yield 'flag_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'hash_b', name_type_map['Uint'], (0, None), (False, None)
		yield 'hash_c', name_type_map['Uint'], (0, None), (False, None)
		yield 'zero_4', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 19:
			yield 'u_2', name_type_map['Uint'], (0, None), (False, None)
			yield 'u_1', name_type_map['Uint'], (0, None), (False, None)
