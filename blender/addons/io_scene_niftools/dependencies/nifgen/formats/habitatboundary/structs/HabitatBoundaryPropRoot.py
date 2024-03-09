from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HabitatBoundaryPropRoot(MemStruct):

	"""
	144 bytes
	"""

	__name__ = 'HabitatBoundaryPropRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 0 = Habitat, 1 = Ride, 2 = Guest
		self.type = name_type_map['Uint64'](self.context, 0, None)
		self.u_1 = name_type_map['Uint64'](self.context, 0, None)
		self.is_guest = name_type_map['Uint'](self.context, 0, None)
		self.post_position = name_type_map['HbPostPos'](self.context, 0, None)
		self.u_2 = name_type_map['Float'](self.context, 0, None)
		self.door_physics = name_type_map['HbPropPhysics'](self.context, 0, None)
		self.path_physics = name_type_map['HbPropPhysics'](self.context, 0, None)
		self.door_cutout = name_type_map['HbDoorCutout'](self.context, 0, None)
		self.small = name_type_map['Uint'](self.context, 0, None)
		self.height = name_type_map['Float'].from_value(2.0)
		self.prefab = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.post = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.wall = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.path_join_part = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'type', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'prefab', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'post', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'wall', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'is_guest', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'post_position', name_type_map['HbPostPos'], (0, None), (False, None), (None, None)
		yield 'u_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'door_physics', name_type_map['HbPropPhysics'], (0, None), (False, None), (None, None)
		yield 'path_physics', name_type_map['HbPropPhysics'], (0, None), (False, None), (None, None)
		yield 'path_join_part', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'door_cutout', name_type_map['HbDoorCutout'], (0, None), (False, None), (None, None)
		yield 'small', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'height', name_type_map['Float'], (0, None), (False, 2.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'type', name_type_map['Uint64'], (0, None), (False, None)
		yield 'prefab', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'post', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'wall', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'is_guest', name_type_map['Uint'], (0, None), (False, None)
		yield 'post_position', name_type_map['HbPostPos'], (0, None), (False, None)
		yield 'u_2', name_type_map['Float'], (0, None), (False, None)
		yield 'door_physics', name_type_map['HbPropPhysics'], (0, None), (False, None)
		yield 'path_physics', name_type_map['HbPropPhysics'], (0, None), (False, None)
		yield 'path_join_part', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'door_cutout', name_type_map['HbDoorCutout'], (0, None), (False, None)
		yield 'small', name_type_map['Uint'], (0, None), (False, None)
		yield 'height', name_type_map['Float'], (0, None), (False, 2.0)
