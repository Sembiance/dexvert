from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.wmeta.imports import name_type_map


class WmetasbMain(MemStruct):

	"""
	# JWE, PC: 112 bytes
	# PZ, JWE2: 32 bytes
	todo - versioning that catches JWE, needs wmetasb version from fileentry
	"""

	__name__ = 'WmetasbMain'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.hash = name_type_map['Uint'](self.context, 0, None)
		self.unk = name_type_map['Uint'](self.context, 0, None)
		self.events_count = name_type_map['Uint64'](self.context, 0, None)
		self.hashes_count = name_type_map['Uint64'](self.context, 0, None)
		self.media_count = name_type_map['Uint64'](self.context, 0, None)
		self.block_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.media_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.bnk_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.events = name_type_map['ArrayPointer'](self.context, self.events_count, name_type_map['EventEntry'])
		self.hashes = name_type_map['ArrayPointer'](self.context, self.hashes_count, name_type_map['Uint'])
		self.media = name_type_map['ArrayPointer'](self.context, self.media_count, name_type_map['MediaEntry'])
		self.unused_2 = name_type_map['Pointer'](self.context, 0, None)
		self.unused_3 = name_type_map['Pointer'](self.context, 0, None)
		self.unused_4 = name_type_map['Pointer'](self.context, 0, None)
		self.unused_5 = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'block_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'media_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (lambda context: context.version <= 18, None)
		yield 'bnk_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (lambda context: context.version <= 18, None)
		yield 'events', name_type_map['ArrayPointer'], (None, name_type_map['EventEntry']), (False, None), (None, None)
		yield 'events_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'hashes', name_type_map['ArrayPointer'], (None, name_type_map['Uint']), (False, None), (lambda context: context.version <= 18, None)
		yield 'hashes_count', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'media', name_type_map['ArrayPointer'], (None, name_type_map['MediaEntry']), (False, None), (lambda context: context.version <= 18, None)
		yield 'media_count', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'unused_2', name_type_map['Pointer'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'unused_3', name_type_map['Pointer'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'unused_4', name_type_map['Pointer'], (0, None), (False, None), (lambda context: context.version <= 18, None)
		yield 'unused_5', name_type_map['Pointer'], (0, None), (False, None), (lambda context: context.version <= 18, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk', name_type_map['Uint'], (0, None), (False, None)
		yield 'block_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		if instance.context.version <= 18:
			yield 'media_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
			yield 'bnk_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'events', name_type_map['ArrayPointer'], (instance.events_count, name_type_map['EventEntry']), (False, None)
		yield 'events_count', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version <= 18:
			yield 'hashes', name_type_map['ArrayPointer'], (instance.hashes_count, name_type_map['Uint']), (False, None)
			yield 'hashes_count', name_type_map['Uint64'], (0, None), (False, None)
			yield 'media', name_type_map['ArrayPointer'], (instance.media_count, name_type_map['MediaEntry']), (False, None)
			yield 'media_count', name_type_map['Uint64'], (0, None), (False, None)
			yield 'unused_2', name_type_map['Pointer'], (0, None), (False, None)
			yield 'unused_3', name_type_map['Pointer'], (0, None), (False, None)
			yield 'unused_4', name_type_map['Pointer'], (0, None), (False, None)
			yield 'unused_5', name_type_map['Pointer'], (0, None), (False, None)
