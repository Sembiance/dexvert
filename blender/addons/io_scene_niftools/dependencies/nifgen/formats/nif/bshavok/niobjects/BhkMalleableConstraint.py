from nifgen.formats.nif.bshavok.niobjects.BhkConstraint import BhkConstraint
from nifgen.formats.nif.imports import name_type_map


class BhkMalleableConstraint(BhkConstraint):

	"""
	Bethesda extension of hkpMalleableConstraintData. Constraint wrapper used to soften or harden constraints.
	Does not affect angular limits or angular motors.
	"""

	__name__ = 'bhkMalleableConstraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.constraint = name_type_map['BhkMalleableConstraintCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'constraint', name_type_map['BhkMalleableConstraintCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'constraint', name_type_map['BhkMalleableConstraintCInfo'], (0, None), (False, None)
