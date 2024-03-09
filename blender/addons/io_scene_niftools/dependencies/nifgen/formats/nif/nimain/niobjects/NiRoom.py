from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class NiRoom(NiNode):

	"""
	NiRoom objects represent cells in a cell-portal culling system.
	"""

	__name__ = 'NiRoom'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_walls = name_type_map['Uint'](self.context, 0, None)
		self.walls = Array(self.context, 0, name_type_map['NiWall'], (0,), name_type_map['Ref'])
		self.wall_planes = Array(self.context, 0, None, (0,), name_type_map['NiPlane'])
		self.num_in_portals = name_type_map['Uint'](self.context, 0, None)

		# The portals which see into the room.
		self.in_portals = Array(self.context, 0, name_type_map['NiPortal'], (0,), name_type_map['Ptr'])
		self.num_out_portals = name_type_map['Uint'](self.context, 0, None)

		# The portals which see out of the room.
		self.out_portals = Array(self.context, 0, name_type_map['NiPortal'], (0,), name_type_map['Ptr'])
		self.num_fixtures = name_type_map['Uint'](self.context, 0, None)

		# All geometry associated with the room. Seems to be Ref for legacy.
		self.fixtures = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_walls', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'walls', Array, (0, name_type_map['NiWall'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version <= 50528269, None)
		yield 'wall_planes', Array, (0, None, (None,), name_type_map['NiPlane']), (False, None), (lambda context: context.version >= 67108864, None)
		yield 'num_in_portals', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'in_portals', Array, (0, name_type_map['NiPortal'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'num_out_portals', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'out_portals', Array, (0, name_type_map['NiPortal'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'num_fixtures', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'fixtures', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ptr']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_walls', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 50528269:
			yield 'walls', Array, (0, name_type_map['NiWall'], (instance.num_walls,), name_type_map['Ref']), (False, None)
		if instance.context.version >= 67108864:
			yield 'wall_planes', Array, (0, None, (instance.num_walls,), name_type_map['NiPlane']), (False, None)
		yield 'num_in_portals', name_type_map['Uint'], (0, None), (False, None)
		yield 'in_portals', Array, (0, name_type_map['NiPortal'], (instance.num_in_portals,), name_type_map['Ptr']), (False, None)
		yield 'num_out_portals', name_type_map['Uint'], (0, None), (False, None)
		yield 'out_portals', Array, (0, name_type_map['NiPortal'], (instance.num_out_portals,), name_type_map['Ptr']), (False, None)
		yield 'num_fixtures', name_type_map['Uint'], (0, None), (False, None)
		yield 'fixtures', Array, (0, name_type_map['NiAVObject'], (instance.num_fixtures,), name_type_map['Ptr']), (False, None)
