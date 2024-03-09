from nifgen.base_struct import BaseStruct
from nifgen.formats.psi.imports import name_type_map


class UnknownStruct(BaseStruct):

	__name__ = 'UnknownStruct'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_int_1 = name_type_map['Biguint32'](self.context, 0, None)
		self.unknown_int_2 = name_type_map['Biguint32'](self.context, 0, None)

		# Judging by the occuring values it maps back to indices in the Phonemes array (except 'any' and 'garbage').
		self.unknown_ushort = name_type_map['Bigushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_int_1', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'unknown_int_2', name_type_map['Biguint32'], (0, None), (False, None), (None, None)
		yield 'unknown_ushort', name_type_map['Bigushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_int_1', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'unknown_int_2', name_type_map['Biguint32'], (0, None), (False, None)
		yield 'unknown_ushort', name_type_map['Bigushort'], (0, None), (False, None)
