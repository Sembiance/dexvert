from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class MeshDataEpicMickey(BaseStruct):

	__name__ = 'MeshDataEpicMickey'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_1 = name_type_map['Int'](self.context, 0, None)
		self.unknown_2 = name_type_map['Int'](self.context, 0, None)
		self.unknown_3 = name_type_map['Int'](self.context, 0, None)
		self.unknown_4 = name_type_map['Int'](self.context, 0, None)
		self.unknown_5 = name_type_map['Float'](self.context, 0, None)
		self.unknown_6 = name_type_map['Int'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_1', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'unknown_2', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'unknown_3', name_type_map['Int'], (0, None), (False, None), (lambda context: context.user_version > 14, None)
		yield 'unknown_4', name_type_map['Int'], (0, None), (False, None), (lambda context: context.user_version > 3, None)
		yield 'unknown_5', name_type_map['Float'], (0, None), (False, None), (lambda context: context.user_version > 3, None)
		yield 'unknown_6', name_type_map['Int'], (0, None), (False, None), (lambda context: context.user_version > 3, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_1', name_type_map['Int'], (0, None), (False, None)
		yield 'unknown_2', name_type_map['Int'], (0, None), (False, None)
		if instance.context.user_version > 14:
			yield 'unknown_3', name_type_map['Int'], (0, None), (False, None)
		if instance.context.user_version > 3:
			yield 'unknown_4', name_type_map['Int'], (0, None), (False, None)
			yield 'unknown_5', name_type_map['Float'], (0, None), (False, None)
			yield 'unknown_6', name_type_map['Int'], (0, None), (False, None)
