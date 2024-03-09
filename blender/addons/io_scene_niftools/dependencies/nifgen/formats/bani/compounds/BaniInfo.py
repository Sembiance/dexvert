from nifgen.base_struct import BaseStruct
from nifgen.formats.bani.imports import name_type_map


class BaniInfo(BaseStruct):

	"""
	Custom header struct
	"""

	__name__ = 'BaniInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['ZString'](self.context, 0, None)
		self.data = name_type_map['BaniRoot'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['ZString'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['BaniRoot'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['ZString'], (0, None), (False, None)
		yield 'data', name_type_map['BaniRoot'], (0, None), (False, None)
