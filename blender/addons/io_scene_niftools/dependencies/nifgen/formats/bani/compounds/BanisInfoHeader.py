from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bani.imports import name_type_map


class BanisInfoHeader(BaseStruct):

	"""
	Custom header struct
	"""

	__name__ = 'BanisInfoHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_anims = name_type_map['Uint'](self.context, 0, None)
		self.anims = Array(self.context, 0, None, (0,), name_type_map['BaniInfo'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_anims', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'anims', Array, (0, None, (None,), name_type_map['BaniInfo']), (False, None), (None, None)
		yield 'data', name_type_map['BanisRoot'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_anims', name_type_map['Uint'], (0, None), (False, None)
		yield 'anims', Array, (0, None, (instance.num_anims,), name_type_map['BaniInfo']), (False, None)
		yield 'data', name_type_map['BanisRoot'], (0, None), (False, None)
