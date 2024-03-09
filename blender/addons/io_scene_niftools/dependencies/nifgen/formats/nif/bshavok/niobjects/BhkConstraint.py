import nifgen.formats.nif as NifFormat
from nifgen.formats.nif.bshavok.niobjects.BhkSerializable import BhkSerializable
from nifgen.formats.nif.imports import name_type_map


class BhkConstraint(BhkSerializable):

	"""
	Bethesda extension of hkpConstraintData. Base class for all constraints.
	"""

	__name__ = 'bhkConstraint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.constraint_info = name_type_map['BhkConstraintCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'constraint_info', name_type_map['BhkConstraintCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'constraint_info', name_type_map['BhkConstraintCInfo'], (0, None), (False, None)

	def get_transform_a_b(self, parent):
		"""Returns the transform of the first entity relative to the second
		entity. Root is simply a nif block that is a common parent to both
		blocks."""
		# check entities
		if self.num_entities != 2:
			raise ValueError(
				"cannot get tranform for constraint "
				"that hasn't exactly 2 entities")
		# find transform of entity A relative to entity B

		# find chains from parent to A and B entities
		chainA = parent.find_chain(self.entities[0])
		chainB = parent.find_chain(self.entities[1])
		# validate the chains
		assert(isinstance(chainA[-1], NifFormat.classes.BhkRigidBody))
		assert(isinstance(chainA[-2], NifFormat.classes.NiCollisionObject))
		assert(isinstance(chainA[-3], NifFormat.classes.NiNode))
		assert(isinstance(chainB[-1], NifFormat.classes.BhkRigidBody))
		assert(isinstance(chainB[-2], NifFormat.classes.NiCollisionObject))
		assert(isinstance(chainB[-3], NifFormat.classes.NiNode))
		# return the relative transform
		return (chainA[-3].get_transform(relative_to = parent)
				* chainB[-3].get_transform(relative_to = parent).get_inverse())

	def update_a_b(self, parent):
		"""Update the B data from the A data. The parent argument is simply a
		common parent to the entities."""
		self.constraint.update_a_b(self.get_transform_a_b(parent))

	def apply_scale(self, scale):
		"""Scale data."""
		super().apply_scale(scale)
		self.constraint.apply_scale(scale)

