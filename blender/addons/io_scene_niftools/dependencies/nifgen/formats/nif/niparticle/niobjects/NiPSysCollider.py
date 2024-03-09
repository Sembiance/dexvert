from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSysCollider(NiObject):

	"""
	Particle system collider.
	"""

	__name__ = 'NiPSysCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Amount of bounce for the collider.
		self.bounce = name_type_map['Float'].from_value(1.0)

		# Spawn particles on impact?
		self.spawn_on_collide = name_type_map['Bool'](self.context, 0, None)

		# Kill particles on impact?
		self.die_on_collide = name_type_map['Bool'](self.context, 0, None)

		# Spawner to use for the collider.
		self.spawn_modifier = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysSpawnModifier'])

		# Link to parent.
		self.parent = name_type_map['Ptr'](self.context, 0, name_type_map['NiPSysColliderManager'])

		# The next collider.
		self.next_collider = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysCollider'])

		# The object whose position and orientation are the basis of the collider.
		self.collider_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounce', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'spawn_on_collide', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'die_on_collide', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'spawn_modifier', name_type_map['Ref'], (0, name_type_map['NiPSysSpawnModifier']), (False, None), (None, None)
		yield 'parent', name_type_map['Ptr'], (0, name_type_map['NiPSysColliderManager']), (False, None), (None, None)
		yield 'next_collider', name_type_map['Ref'], (0, name_type_map['NiPSysCollider']), (False, None), (None, None)
		yield 'collider_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bounce', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'spawn_on_collide', name_type_map['Bool'], (0, None), (False, None)
		yield 'die_on_collide', name_type_map['Bool'], (0, None), (False, None)
		yield 'spawn_modifier', name_type_map['Ref'], (0, name_type_map['NiPSysSpawnModifier']), (False, None)
		yield 'parent', name_type_map['Ptr'], (0, name_type_map['NiPSysColliderManager']), (False, None)
		yield 'next_collider', name_type_map['Ref'], (0, name_type_map['NiPSysCollider']), (False, None)
		yield 'collider_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
