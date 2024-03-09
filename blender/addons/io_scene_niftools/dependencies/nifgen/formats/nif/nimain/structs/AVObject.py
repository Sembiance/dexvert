from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class AVObject(BaseStruct):

	"""
	Used in NiDefaultAVObjectPalette.
	"""

	__name__ = 'AVObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Object name.
		self.name = name_type_map['SizedString'](self.context, 0, None)

		# Object reference.
		self.av_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'av_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['SizedString'], (0, None), (False, None)
		yield 'av_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
