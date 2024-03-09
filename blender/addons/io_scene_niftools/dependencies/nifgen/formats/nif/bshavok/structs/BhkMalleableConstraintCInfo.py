from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkMalleableConstraintCInfo(BaseStruct):

	"""
	bhkMalleableConstraint serialization data. A constraint wrapper used to soften or harden constraints.
	"""

	__name__ = 'bhkMalleableConstraintCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Type of constraint.
		self.type = name_type_map['HkConstraintType'](self.context, 0, None)
		self.constraint_info = name_type_map['BhkConstraintCInfo'](self.context, 0, None)
		self.ball_and_socket = name_type_map['BhkBallAndSocketConstraintCInfo'](self.context, 0, None)
		self.hinge = name_type_map['BhkHingeConstraintCInfo'](self.context, 0, None)
		self.limited_hinge = name_type_map['BhkLimitedHingeConstraintCInfo'](self.context, 0, None)
		self.prismatic = name_type_map['BhkPrismaticConstraintCInfo'](self.context, 0, None)
		self.ragdoll = name_type_map['BhkRagdollConstraintCInfo'](self.context, 0, None)
		self.stiff_spring = name_type_map['BhkStiffSpringConstraintCInfo'](self.context, 0, None)
		self.tau = name_type_map['Float'](self.context, 0, None)
		self.damping = name_type_map['Float'](self.context, 0, None)
		self.strength = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'type', name_type_map['HkConstraintType'], (0, None), (False, None), (None, None)
		yield 'constraint_info', name_type_map['BhkConstraintCInfo'], (0, None), (False, None), (None, None)
		yield 'ball_and_socket', name_type_map['BhkBallAndSocketConstraintCInfo'], (0, None), (False, None), (None, True)
		yield 'hinge', name_type_map['BhkHingeConstraintCInfo'], (0, None), (False, None), (None, True)
		yield 'limited_hinge', name_type_map['BhkLimitedHingeConstraintCInfo'], (0, None), (False, None), (None, True)
		yield 'prismatic', name_type_map['BhkPrismaticConstraintCInfo'], (0, None), (False, None), (None, True)
		yield 'ragdoll', name_type_map['BhkRagdollConstraintCInfo'], (0, None), (False, None), (None, True)
		yield 'stiff_spring', name_type_map['BhkStiffSpringConstraintCInfo'], (0, None), (False, None), (None, True)
		yield 'tau', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'strength', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'type', name_type_map['HkConstraintType'], (0, None), (False, None)
		yield 'constraint_info', name_type_map['BhkConstraintCInfo'], (0, None), (False, None)
		if instance.type == 0:
			yield 'ball_and_socket', name_type_map['BhkBallAndSocketConstraintCInfo'], (0, None), (False, None)
		if instance.type == 1:
			yield 'hinge', name_type_map['BhkHingeConstraintCInfo'], (0, None), (False, None)
		if instance.type == 2:
			yield 'limited_hinge', name_type_map['BhkLimitedHingeConstraintCInfo'], (0, None), (False, None)
		if instance.type == 6:
			yield 'prismatic', name_type_map['BhkPrismaticConstraintCInfo'], (0, None), (False, None)
		if instance.type == 7:
			yield 'ragdoll', name_type_map['BhkRagdollConstraintCInfo'], (0, None), (False, None)
		if instance.type == 8:
			yield 'stiff_spring', name_type_map['BhkStiffSpringConstraintCInfo'], (0, None), (False, None)
		if instance.context.version <= 335544325:
			yield 'tau', name_type_map['Float'], (0, None), (False, None)
			yield 'damping', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335675399:
			yield 'strength', name_type_map['Float'], (0, None), (False, None)

	constraint_fields = ['ball_and_socket',
					     'hinge',
						 'limited_hinge',
						 'prismatic',
						 'ragdoll',
						 'stiff_spring',
						 ]

	def apply_scale(self, scale):
		for field_name in self.constraint_fields:
			getattr(self, field_name).apply_scale(scale)

	def update_a_b(self, transform):
		"""Update B pivot and axes from A using the given transform."""
		for field_name in self.constraint_fields:
			getattr(self, field_name).update_a_b(transform)

