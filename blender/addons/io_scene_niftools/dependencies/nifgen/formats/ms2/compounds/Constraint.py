from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class Constraint(BaseStruct):

	__name__ = 'Constraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.parent = name_type_map['JointPointer'](self.context, 0, None)
		self.child = name_type_map['JointPointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'parent', name_type_map['JointPointer'], (0, None), (False, None), (None, None)
		yield 'child', name_type_map['JointPointer'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'parent', name_type_map['JointPointer'], (0, None), (False, None)
		yield 'child', name_type_map['JointPointer'], (0, None), (False, None)
