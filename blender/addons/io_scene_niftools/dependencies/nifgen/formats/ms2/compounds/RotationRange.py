from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class RotationRange(BaseStruct):

	"""
	tentative interpretation
	"""

	__name__ = 'RotationRange'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.min = name_type_map['Float'](self.context, 0, None)
		self.max = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'min', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'min', name_type_map['Float'], (0, None), (False, None)
		yield 'max', name_type_map['Float'], (0, None), (False, None)
