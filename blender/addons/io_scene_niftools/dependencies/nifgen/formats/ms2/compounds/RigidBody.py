from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class RigidBody(BaseStruct):

	__name__ = 'RigidBody'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 2 kinematic, 0 1 static
		self.flag = name_type_map['Uint'](self.context, 0, None)

		# center of mass - from the head of the bone the collider is attached to
		self.loc = name_type_map['Vector3'](self.context, 0, None)

		# mass of joint or object
		self.mass = name_type_map['Float'](self.context, 0, None)

		# coefficient of static friction(small wants to roll, larger wants to slide)
		self.static_friction = name_type_map['Float'](self.context, 0, None)

		# 2.0 in unk1 makes the object not to stop ever, it is breakdancing
		self.unk_1 = name_type_map['Float'](self.context, 0, None)

		# Related to Bounciness
		self.unk_2 = name_type_map['Float'](self.context, 0, None)

		# NOT air resistance
		self.unknown_friction = name_type_map['Float'](self.context, 0, None)

		# ?
		self.unk_4 = name_type_map['Float'](self.context, 0, None)

		# coefficient of dynamic friction
		self.dynamic_friction = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flag', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'static_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_4', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'dynamic_friction', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flag', name_type_map['Uint'], (0, None), (False, None)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, None)
		yield 'static_friction', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_1', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_2', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown_friction', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_4', name_type_map['Float'], (0, None), (False, None)
		yield 'dynamic_friction', name_type_map['Float'], (0, None), (False, None)
