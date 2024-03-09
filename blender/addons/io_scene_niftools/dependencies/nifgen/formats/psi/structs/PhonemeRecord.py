from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.psi.imports import name_type_map


class PhonemeRecord(BaseStruct):

	"""
	Note: order of the arg-dependent fields is not conclusively determined because it's difficult to determine which ushort is which.
	"""

	__name__ = 'PhonemeRecord'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['SizedString'](self.context, 0, name_type_map['Bigushort'])
		self.type = name_type_map['Ubyte'](self.context, 0, None)
		self.value = name_type_map['Bigushort'](self.context, 0, None)
		self.ushorts_1 = Array(self.context, 0, None, (0,), name_type_map['Bigushort'])
		self.ushorts_2 = Array(self.context, 0, None, (0,), name_type_map['Bigushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['SizedString'], (0, name_type_map['Bigushort']), (False, None), (None, None)
		yield 'type', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'value', name_type_map['Bigushort'], (0, None), (False, None), (None, True)
		yield 'ushorts_1', Array, (0, None, (None,), name_type_map['Bigushort']), (False, None), (None, True)
		yield 'ushorts_2', Array, (0, None, (None,), name_type_map['Bigushort']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['SizedString'], (0, name_type_map['Bigushort']), (False, None)
		yield 'type', name_type_map['Ubyte'], (0, None), (False, None)
		if instance.type & 1:
			yield 'value', name_type_map['Bigushort'], (0, None), (False, None)
		if instance.type & 2:
			yield 'ushorts_1', Array, (0, None, (instance.arg,), name_type_map['Bigushort']), (False, None)
		if instance.type & 4:
			yield 'ushorts_2', Array, (0, None, (instance.arg,), name_type_map['Bigushort']), (False, None)
