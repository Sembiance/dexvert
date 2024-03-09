from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkConstraintChainCInfo(BaseStruct):

	"""
	Bethesda extension of hkpConstraintChainInstance.
	"""

	__name__ = 'bhkConstraintChainCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_chained_entities = name_type_map['Uint'](self.context, 0, None)
		self.chained_entities = Array(self.context, 0, name_type_map['BhkRigidBody'], (0,), name_type_map['Ptr'])
		self.constraint_info = name_type_map['BhkConstraintCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_chained_entities', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'chained_entities', Array, (0, name_type_map['BhkRigidBody'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'constraint_info', name_type_map['BhkConstraintCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_chained_entities', name_type_map['Uint'], (0, None), (False, None)
		yield 'chained_entities', Array, (0, name_type_map['BhkRigidBody'], (instance.num_chained_entities,), name_type_map['Ptr']), (False, None)
		yield 'constraint_info', name_type_map['BhkConstraintCInfo'], (0, None), (False, None)
