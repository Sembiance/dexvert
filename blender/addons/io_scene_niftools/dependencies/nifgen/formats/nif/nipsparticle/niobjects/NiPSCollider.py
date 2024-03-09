from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSCollider(NiObject):

	"""
	Abstract base class for all particle colliders.
	"""

	__name__ = 'NiPSCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.spawner = name_type_map['Ref'](self.context, 0, name_type_map['NiPSSpawner'])
		self.type = name_type_map['ColliderType'](self.context, 0, None)
		self.active = name_type_map['Bool'](self.context, 0, None)
		self.bounce = name_type_map['Float'].from_value(1.0)
		self.spawn_on_collide = name_type_map['Bool'](self.context, 0, None)
		self.die_on_collide = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'spawner', name_type_map['Ref'], (0, name_type_map['NiPSSpawner']), (False, None), (None, None)
		yield 'type', name_type_map['ColliderType'], (0, None), (False, None), (None, None)
		yield 'active', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'bounce', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'spawn_on_collide', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'die_on_collide', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'spawner', name_type_map['Ref'], (0, name_type_map['NiPSSpawner']), (False, None)
		yield 'type', name_type_map['ColliderType'], (0, None), (False, None)
		yield 'active', name_type_map['Bool'], (0, None), (False, None)
		yield 'bounce', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'spawn_on_collide', name_type_map['Bool'], (0, None), (False, None)
		yield 'die_on_collide', name_type_map['Bool'], (0, None), (False, None)
