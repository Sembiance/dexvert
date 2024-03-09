from nifgen.formats.ms2.compounds.Constraint import Constraint
from nifgen.formats.ms2.imports import name_type_map


class StretchConstraint(Constraint):

	"""
	used in JWE dinos
	no longer used in PZ, JWE2
	"""

	__name__ = 'StretchConstraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# location of the joint
		self.loc = name_type_map['Vector3'](self.context, 0, None)

		# normalized
		self.direction = name_type_map['Vector3'](self.context, 0, None)

		# min, le 0
		self.min = name_type_map['Float'](self.context, 0, None)

		# max, ge 0
		self.max = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'min', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None)
		yield 'min', name_type_map['Float'], (0, None), (False, None)
		yield 'max', name_type_map['Float'], (0, None), (False, None)
