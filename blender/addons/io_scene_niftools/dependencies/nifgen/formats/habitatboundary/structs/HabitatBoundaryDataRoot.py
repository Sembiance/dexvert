from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HabitatBoundaryDataRoot(MemStruct):

	"""
	224 bytes
	"""

	__name__ = 'HabitatBoundaryDataRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 3 for everything but null barrier which is 0
		self.u_1 = name_type_map['Uint'].from_value(3)
		self.u_2 = name_type_map['Float'](self.context, 0, None)

		# 0 for everything but wood logs barrier which is 1
		self.u_3 = name_type_map['Ushort'].from_value(0)
		self.ui_options = name_type_map['HbUiOptions'](self.context, 0, None)
		self.u_4 = name_type_map['Float'].from_value(1.5)
		self.u_5 = name_type_map['Float'].from_value(2.5)
		self.offsets = name_type_map['HbOffsets'](self.context, 0, None)

		# Posts of N Level can only use Walls of less than N Level
		self.wall_replace_level = name_type_map['Byte'](self.context, 0, None)

		# 0 = Glass, 1 = Null, 3 = Solid Opaques (Brick, Concrete), 4 = 1-Way Glass, 5 = Wire Fences, 7 = Electrified Wire Fence
		self.type = name_type_map['Byte'](self.context, 0, None)
		self.padding = name_type_map['Ushort'].from_value(0)
		self.prefab = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion_end = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion_top = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion_cap_top = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion_bottom = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_unk_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_unk_3 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_unk_4 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion_door_cap_side = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion_door_cap_end = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.walls_extrusion_door_cap_underside = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.climb_proof_data = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.broken_post = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.broken_extrusion = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.broken_extrusion_pile = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.broken_ground = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.broken_1_m = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.broken_10_m = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.post = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.post_cap = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'prefab', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion_end', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion_top', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion_cap_top', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion_bottom', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_unk_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_unk_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_unk_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion_door_cap_side', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion_door_cap_end', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'walls_extrusion_door_cap_underside', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'climb_proof_data', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'broken_post', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'broken_extrusion', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'broken_extrusion_pile', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'broken_ground', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'broken_1_m', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'broken_10_m', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'post', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'post_cap', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'u_1', name_type_map['Uint'], (0, None), (False, 3), (None, None)
		yield 'u_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_3', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'ui_options', name_type_map['HbUiOptions'], (0, None), (False, None), (None, None)
		yield 'u_4', name_type_map['Float'], (0, None), (False, 1.5), (None, None)
		yield 'u_5', name_type_map['Float'], (0, None), (False, 2.5), (None, None)
		yield 'offsets', name_type_map['HbOffsets'], (0, None), (False, None), (None, None)
		yield 'wall_replace_level', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'type', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'padding', name_type_map['Ushort'], (0, None), (True, 0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'prefab', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion_end', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion_top', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion_cap_top', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion_bottom', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_unk_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_unk_3', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_unk_4', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion_door_cap_side', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion_door_cap_end', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'walls_extrusion_door_cap_underside', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'climb_proof_data', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'broken_post', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'broken_extrusion', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'broken_extrusion_pile', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'broken_ground', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'broken_1_m', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'broken_10_m', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'post', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'post_cap', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'u_1', name_type_map['Uint'], (0, None), (False, 3)
		yield 'u_2', name_type_map['Float'], (0, None), (False, None)
		yield 'u_3', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'ui_options', name_type_map['HbUiOptions'], (0, None), (False, None)
		yield 'u_4', name_type_map['Float'], (0, None), (False, 1.5)
		yield 'u_5', name_type_map['Float'], (0, None), (False, 2.5)
		yield 'offsets', name_type_map['HbOffsets'], (0, None), (False, None)
		yield 'wall_replace_level', name_type_map['Byte'], (0, None), (False, None)
		yield 'type', name_type_map['Byte'], (0, None), (False, None)
		yield 'padding', name_type_map['Ushort'], (0, None), (True, 0)
