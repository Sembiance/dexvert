from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class ZTPreBones(BaseStruct):

	__name__ = 'ZTPreBones'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint64'])
		self.unks = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.unks_2 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.unks_3 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None), (None, None)
		yield 'unks', Array, (0, None, (8,), name_type_map['Uint']), (False, None), (None, None)
		yield 'unks_2', Array, (0, None, (10,), name_type_map['Uint']), (False, None), (None, None)
		yield 'floats', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, None)
		yield 'unks_3', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None)
		yield 'unks', Array, (0, None, (8,), name_type_map['Uint']), (False, None)
		yield 'unks_2', Array, (0, None, (10,), name_type_map['Uint']), (False, None)
		yield 'floats', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		yield 'unks_3', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
