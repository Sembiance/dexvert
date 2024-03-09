from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class WeirdElementOne(BaseStruct):

	__name__ = 'WeirdElementOne'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.float_0 = name_type_map['Float'](self.context, 0, None)
		self.vec_0 = name_type_map['Vector3'](self.context, 0, None)
		self.zeros_0 = Array(self.context, 0, None, (0,), name_type_map['Uint64'])
		self.vec_1 = name_type_map['Vector3'](self.context, 0, None)
		self.countb = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'float_0', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'vec_0', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'zeros_0', Array, (0, None, (2,), name_type_map['Uint64']), (False, None), (None, None)
		yield 'vec_1', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'countb', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'float_0', name_type_map['Float'], (0, None), (False, None)
		yield 'vec_0', name_type_map['Vector3'], (0, None), (False, None)
		yield 'zeros_0', Array, (0, None, (2,), name_type_map['Uint64']), (False, None)
		yield 'vec_1', name_type_map['Vector3'], (0, None), (False, None)
		yield 'countb', name_type_map['Uint'], (0, None), (False, None)
