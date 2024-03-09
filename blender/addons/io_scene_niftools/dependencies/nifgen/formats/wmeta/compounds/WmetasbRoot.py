from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.wmeta.imports import name_type_map


class WmetasbRoot(MemStruct):

	__name__ = 'WmetasbRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.levels = name_type_map['ArrayPointer'](self.context, self.count, name_type_map['WmetasbMain'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'levels', name_type_map['ArrayPointer'], (None, name_type_map['Jwe2WmetasbMain']), (False, None), (lambda context: context.user_version.use_djb and (context.version == 20), None)
		yield 'levels', name_type_map['ArrayPointer'], (None, name_type_map['WmetasbMain']), (False, None), (lambda context: not (context.user_version.use_djb and (context.version == 20)), None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.user_version.use_djb and (instance.context.version == 20):
			yield 'levels', name_type_map['ArrayPointer'], (instance.count, name_type_map['Jwe2WmetasbMain']), (False, None)
		if not (instance.context.user_version.use_djb and (instance.context.version == 20)):
			yield 'levels', name_type_map['ArrayPointer'], (instance.count, name_type_map['WmetasbMain']), (False, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)
