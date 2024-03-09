from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkSerializable import BhkSerializable
from nifgen.formats.nif.imports import name_type_map


class BhkBallSocketConstraintChain(BhkSerializable):

	"""
	Bethesda extension of hkpBallSocketChainData. A chain of ball and socket constraints.
	"""

	__name__ = 'bhkBallSocketConstraintChain'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Should equal (Num Chained Entities - 1) * 2
		self.num_pivots = name_type_map['Uint'](self.context, 0, None)

		# Two pivot points A and B for each constraint.
		self.pivots = Array(self.context, 0, None, (0,), name_type_map['BhkBallAndSocketConstraintCInfo'])

		# High values are harder and more reactive, lower values are smoother.
		self.tau = name_type_map['Float'].from_value(1.0)

		# Defines damping strength for the current velocity.
		self.damping = name_type_map['Float'].from_value(0.6)

		# Restitution (amount of elasticity) of constraints. Added to the diagonal of the constraint matrix. A value of 0.0 can result in a division by zero with some chain configurations.
		self.constraint_force_mixing = name_type_map['Float'].from_value(1.1920929e-08)

		# Maximum distance error in constraints allowed before stabilization algorithm kicks in. A smaller distance causes more resistance.
		self.max_error_distance = name_type_map['Float'].from_value(0.1)
		self.constraint_chain_info = name_type_map['BhkConstraintChainCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_pivots', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'pivots', Array, (0, None, (None,), name_type_map['BhkBallAndSocketConstraintCInfo']), (False, None), (None, None)
		yield 'tau', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, 0.6), (None, None)
		yield 'constraint_force_mixing', name_type_map['Float'], (0, None), (False, 1.1920929e-08), (None, None)
		yield 'max_error_distance', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'constraint_chain_info', name_type_map['BhkConstraintChainCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_pivots', name_type_map['Uint'], (0, None), (False, None)
		yield 'pivots', Array, (0, None, (int(instance.num_pivots / 2),), name_type_map['BhkBallAndSocketConstraintCInfo']), (False, None)
		yield 'tau', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'damping', name_type_map['Float'], (0, None), (False, 0.6)
		yield 'constraint_force_mixing', name_type_map['Float'], (0, None), (False, 1.1920929e-08)
		yield 'max_error_distance', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'constraint_chain_info', name_type_map['BhkConstraintChainCInfo'], (0, None), (False, None)
