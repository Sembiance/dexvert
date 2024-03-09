from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXJointDesc(NiObject):

	"""
	A PhysX Joint abstract base class.
	"""

	__name__ = 'NiPhysXJointDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.joint_type = name_type_map['NxJointType'](self.context, 0, None)
		self.joint_name = name_type_map['NiFixedString'](self.context, 0, None)
		self.actors = Array(self.context, 0, None, (0,), name_type_map['NiPhysXJointActor'])
		self.max_force = name_type_map['Float'](self.context, 0, None)
		self.max_torque = name_type_map['Float'](self.context, 0, None)
		self.solver_extrapolation_factor = name_type_map['Float'](self.context, 0, None)
		self.use_acceleration_spring = name_type_map['Uint'](self.context, 0, None)
		self.joint_flags = name_type_map['Uint'](self.context, 0, None)
		self.limit_point = name_type_map['Vector3'](self.context, 0, None)
		self.num_limits = name_type_map['Uint'](self.context, 0, None)
		self.limits = Array(self.context, 0, None, (0,), name_type_map['NiPhysXJointLimit'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'joint_type', name_type_map['NxJointType'], (0, None), (False, None), (None, None)
		yield 'joint_name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'actors', Array, (0, None, (2,), name_type_map['NiPhysXJointActor']), (False, None), (None, None)
		yield 'max_force', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'max_torque', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'solver_extrapolation_factor', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335872003, None)
		yield 'use_acceleration_spring', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335872003, None)
		yield 'joint_flags', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'limit_point', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'num_limits', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'limits', Array, (0, None, (None,), name_type_map['NiPhysXJointLimit']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'joint_type', name_type_map['NxJointType'], (0, None), (False, None)
		yield 'joint_name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'actors', Array, (0, None, (2,), name_type_map['NiPhysXJointActor']), (False, None)
		yield 'max_force', name_type_map['Float'], (0, None), (False, None)
		yield 'max_torque', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335872003:
			yield 'solver_extrapolation_factor', name_type_map['Float'], (0, None), (False, None)
			yield 'use_acceleration_spring', name_type_map['Uint'], (0, None), (False, None)
		yield 'joint_flags', name_type_map['Uint'], (0, None), (False, None)
		yield 'limit_point', name_type_map['Vector3'], (0, None), (False, None)
		yield 'num_limits', name_type_map['Uint'], (0, None), (False, None)
		yield 'limits', Array, (0, None, (instance.num_limits,), name_type_map['NiPhysXJointLimit']), (False, None)
