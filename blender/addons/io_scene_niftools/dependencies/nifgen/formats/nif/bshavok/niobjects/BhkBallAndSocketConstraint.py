from nifgen.formats.nif.bshavok.niobjects.BhkConstraint import BhkConstraint
from nifgen.formats.nif.imports import name_type_map


class BhkBallAndSocketConstraint(BhkConstraint):

	"""
	Bethesda extension of hkpBallAndSocketConstraintData.
	Point-to-point constraint that attempts to keep the pivot point of two bodies in the same space.
	"""

	__name__ = 'bhkBallAndSocketConstraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.constraint = name_type_map['BhkBallAndSocketConstraintCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'constraint', name_type_map['BhkBallAndSocketConstraintCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'constraint', name_type_map['BhkBallAndSocketConstraintCInfo'], (0, None), (False, None)
