from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkConstraintCInfo(BaseStruct):

	"""
	Bethesda extension of hkpConstraintInstance.
	"""

	__name__ = 'bhkConstraintCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Always 2 (Hardcoded). Number of bodies affected by this constraint.
		self.num_entities = name_type_map['Uint'].from_value(2)

		# The entity affected by this constraint.
		self.entity_a = name_type_map['Ptr'](self.context, 0, name_type_map['BhkEntity'])

		# The entity affected by this constraint.
		self.entity_b = name_type_map['Ptr'](self.context, 0, name_type_map['BhkEntity'])

		# Either PSI or TOI priority. TOI is higher priority.
		self.priority = name_type_map['ConstraintPriority'].PRIORITY_PSI
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_entities', name_type_map['Uint'], (0, None), (False, 2), (None, None)
		yield 'entity_a', name_type_map['Ptr'], (0, name_type_map['BhkEntity']), (False, None), (None, None)
		yield 'entity_b', name_type_map['Ptr'], (0, name_type_map['BhkEntity']), (False, None), (None, None)
		yield 'priority', name_type_map['ConstraintPriority'], (0, None), (False, name_type_map['ConstraintPriority'].PRIORITY_PSI), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_entities', name_type_map['Uint'], (0, None), (False, 2)
		yield 'entity_a', name_type_map['Ptr'], (0, name_type_map['BhkEntity']), (False, None)
		yield 'entity_b', name_type_map['Ptr'], (0, name_type_map['BhkEntity']), (False, None)
		yield 'priority', name_type_map['ConstraintPriority'], (0, None), (False, name_type_map['ConstraintPriority'].PRIORITY_PSI)
