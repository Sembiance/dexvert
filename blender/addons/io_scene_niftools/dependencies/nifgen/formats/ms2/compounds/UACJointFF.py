from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class UACJointFF(BaseStruct):

	__name__ = 'UACJointFF'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# must be 11
		self.eleven = name_type_map['Uint'](self.context, 0, None)

		# bunch of -1's, and constants
		self.f_fs = Array(self.context, 0, None, (0,), name_type_map['Int'])
		self.name = name_type_map['OffsetString'](self.context, self.arg, None)
		self.hitcheck_count = name_type_map['Uint'](self.context, 0, None)

		# 12 bytes of zeros
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'eleven', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'f_fs', Array, (0, None, (4,), name_type_map['Int']), (False, None), (None, None)
		yield 'name', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'hitcheck_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'eleven', name_type_map['Uint'], (0, None), (False, None)
		yield 'f_fs', Array, (0, None, (4,), name_type_map['Int']), (False, None)
		yield 'name', name_type_map['OffsetString'], (instance.arg, None), (False, None)
		yield 'hitcheck_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, None)
