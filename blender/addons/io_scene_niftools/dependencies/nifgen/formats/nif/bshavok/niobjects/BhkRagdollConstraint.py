from nifgen.formats.nif.bshavok.niobjects.BhkConstraint import BhkConstraint
from nifgen.formats.nif.imports import name_type_map


class BhkRagdollConstraint(BhkConstraint):

	"""
	Bethesda extension of hkpRagdollConstraintData. Creates a joint between two bodies with 3 degrees of freedom and a motor.
	Enabling the motor will remove any friction.
	The area of movement can be represented as a main cone + 2 orthogonal cones which may subtract from the main cone volume depending on limits.
	"""

	__name__ = 'bhkRagdollConstraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.constraint = name_type_map['BhkRagdollConstraintCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'constraint', name_type_map['BhkRagdollConstraintCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'constraint', name_type_map['BhkRagdollConstraintCInfo'], (0, None), (False, None)
