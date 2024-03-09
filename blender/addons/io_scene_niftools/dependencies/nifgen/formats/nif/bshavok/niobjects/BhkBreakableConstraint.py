from nifgen.formats.nif.bshavok.niobjects.BhkConstraint import BhkConstraint
from nifgen.formats.nif.imports import name_type_map


class BhkBreakableConstraint(BhkConstraint):

	"""
	Bethesda extension of hkpBreakableConstraintData, a wrapper around hkpConstraintInstance.
	The constraint can "break" i.e. stop applying the forces to each body to keep them constrained.
	"""

	__name__ = 'bhkBreakableConstraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The wrapped constraint.
		self.constraint_data = name_type_map['BhkWrappedConstraintData'](self.context, 0, None)

		# The larger the value, the harder to "break" the constraint.
		self.threshold = name_type_map['Float'](self.context, 0, None)

		# No: Constraint stays active. Yes: Constraint gets removed when breaking threshold is exceeded.
		self.remove_when_broken = name_type_map['Bool'].from_value(False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'constraint_data', name_type_map['BhkWrappedConstraintData'], (0, None), (False, None), (None, None)
		yield 'threshold', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'remove_when_broken', name_type_map['Bool'], (0, None), (False, False), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'constraint_data', name_type_map['BhkWrappedConstraintData'], (0, None), (False, None)
		yield 'threshold', name_type_map['Float'], (0, None), (False, None)
		yield 'remove_when_broken', name_type_map['Bool'], (0, None), (False, False)
