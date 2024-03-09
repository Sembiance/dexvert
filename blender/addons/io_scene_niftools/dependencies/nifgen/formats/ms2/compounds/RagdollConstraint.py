from nifgen.array import Array
from nifgen.formats.ms2.compounds.Constraint import Constraint
from nifgen.formats.ms2.imports import name_type_map


class RagdollConstraint(Constraint):

	"""
	probably ragdoll, lots of angles
	"""

	__name__ = 'RagdollConstraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# the location of the child joint
		self.loc = name_type_map['Vector3'](self.context, 0, None)

		# each of the vec3 components is normalized, these might represent axes for the angles
		self.floats = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# radians
		self.radians = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'floats', Array, (0, None, (5, 3,), name_type_map['Float']), (False, None), (None, None)
		yield 'radians', Array, (0, None, (8,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None)
		yield 'floats', Array, (0, None, (5, 3,), name_type_map['Float']), (False, None)
		yield 'radians', Array, (0, None, (8,), name_type_map['Float']), (False, None)
