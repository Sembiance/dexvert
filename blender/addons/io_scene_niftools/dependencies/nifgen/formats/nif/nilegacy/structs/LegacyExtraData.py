from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class LegacyExtraData(BaseStruct):

	"""
	Extra Data for pre-3.0 versions
	"""

	__name__ = 'LegacyExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.has_extra_data = name_type_map['Bool'](self.context, 0, None)
		self.extra_prop_name = name_type_map['SizedString'](self.context, 0, None)
		self.extra_ref_id = name_type_map['Uint'](self.context, 0, None)
		self.extra_string = name_type_map['SizedString'](self.context, 0, None)
		self.unknown_byte_1 = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_extra_data', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'extra_prop_name', name_type_map['SizedString'], (0, None), (False, None), (None, True)
		yield 'extra_ref_id', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'extra_string', name_type_map['SizedString'], (0, None), (False, None), (None, True)
		yield 'unknown_byte_1', name_type_map['Byte'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_extra_data', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_extra_data:
			yield 'extra_prop_name', name_type_map['SizedString'], (0, None), (False, None)
			yield 'extra_ref_id', name_type_map['Uint'], (0, None), (False, None)
			yield 'extra_string', name_type_map['SizedString'], (0, None), (False, None)
		yield 'unknown_byte_1', name_type_map['Byte'], (0, None), (False, None)
