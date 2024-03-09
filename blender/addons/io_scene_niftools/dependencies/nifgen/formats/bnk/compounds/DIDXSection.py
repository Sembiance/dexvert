from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class DIDXSection(BaseStruct):

	"""
	second Section of a soundback aux
	"""

	__name__ = 'DIDXSection'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# length of following data
		self.length = name_type_map['Uint'](self.context, 0, None)
		self.data_pointers = Array(self.context, 0, None, (0,), name_type_map['DataPointer'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data_pointers', Array, (0, None, (None,), name_type_map['DataPointer']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Uint'], (0, None), (False, None)
		yield 'data_pointers', Array, (0, None, (int(instance.length / 12),), name_type_map['DataPointer']), (False, None)
