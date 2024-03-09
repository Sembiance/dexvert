from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXClothDesc(NiObject):

	"""
	For serializing NxClothDesc objects.
	"""

	__name__ = 'NiPhysXClothDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['NiFixedString'](self.context, 0, None)
		self.mesh = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXMeshDesc'])
		self.pose = name_type_map['Matrix34'](self.context, 0, None)
		self.thickness = name_type_map['Float'].from_value(0.01)
		self.self_collision_thickness = name_type_map['Float'](self.context, 0, None)
		self.density = name_type_map['Float'].from_value(1.0)
		self.bending_stiffness = name_type_map['Float'].from_value(1.0)
		self.stretching_stiffness = name_type_map['Float'].from_value(1.0)
		self.damping_coefficient = name_type_map['Float'].from_value(0.5)
		self.hard_stretch_limitation_factor = name_type_map['Float'](self.context, 0, None)
		self.friction = name_type_map['Float'].from_value(0.5)
		self.pressure = name_type_map['Float'].from_value(1.0)
		self.tear_factor = name_type_map['Float'].from_value(1.5)
		self.collision_response_coeff = name_type_map['Float'].from_value(0.2)
		self.attach_response_coeff = name_type_map['Float'].from_value(0.2)
		self.attach_tear_factor = name_type_map['Float'].from_value(1.5)
		self.to_fluid_response_coeff = name_type_map['Float'].from_value(1.0)
		self.from_fluid_response_coeff = name_type_map['Float'].from_value(1.0)
		self.min_adhere_velocity = name_type_map['Float'].from_value(1.0)
		self.relative_grid_spacing = name_type_map['Float'].from_value(0.25)
		self.solver_iterations = name_type_map['Uint'].from_value(5)
		self.hier_solver_iterations = name_type_map['Uint'](self.context, 0, None)
		self.external_acceleration = name_type_map['Vector3'](self.context, 0, None)
		self.wind_acceleration = name_type_map['Vector3'](self.context, 0, None)
		self.wake_up_counter = name_type_map['Float'].from_value(0.4)
		self.sleep_linear_velocity = name_type_map['Float'].from_value(-1.0)
		self.collision_group = name_type_map['Ushort'](self.context, 0, None)
		self.collision_bits = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.force_field_material = name_type_map['Ushort'](self.context, 0, None)
		self.flags = name_type_map['NxClothFlag'].from_value(32)
		self.vertex_map_size = name_type_map['Ushort'](self.context, 0, None)
		self.vertex_map = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.num_states = name_type_map['Uint'](self.context, 0, None)
		self.states = Array(self.context, 0, None, (0,), name_type_map['PhysXClothState'])
		self.num_attachments = name_type_map['Uint'](self.context, 0, None)
		self.attachments = Array(self.context, 0, None, (0,), name_type_map['PhysXClothAttachment'])
		self.parent_actor = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXActorDesc'])
		self.dest = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXDest'])
		self.target_mesh = name_type_map['Ref'](self.context, 0, name_type_map['NiMesh'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'mesh', name_type_map['Ref'], (0, name_type_map['NiPhysXMeshDesc']), (False, None), (None, None)
		yield 'pose', name_type_map['Matrix34'], (0, None), (False, None), (lambda context: context.version <= 335740937, None)
		yield 'thickness', name_type_map['Float'], (0, None), (False, 0.01), (None, None)
		yield 'self_collision_thickness', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 503382019, None)
		yield 'density', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'bending_stiffness', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'stretching_stiffness', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'damping_coefficient', name_type_map['Float'], (0, None), (False, 0.5), (None, None)
		yield 'hard_stretch_limitation_factor', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 503382019, None)
		yield 'friction', name_type_map['Float'], (0, None), (False, 0.5), (None, None)
		yield 'pressure', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'tear_factor', name_type_map['Float'], (0, None), (False, 1.5), (None, None)
		yield 'collision_response_coeff', name_type_map['Float'], (0, None), (False, 0.2), (None, None)
		yield 'attach_response_coeff', name_type_map['Float'], (0, None), (False, 0.2), (None, None)
		yield 'attach_tear_factor', name_type_map['Float'], (0, None), (False, 1.5), (None, None)
		yield 'to_fluid_response_coeff', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.version >= 335806464, None)
		yield 'from_fluid_response_coeff', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.version >= 335806464, None)
		yield 'min_adhere_velocity', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.version >= 335806464, None)
		yield 'relative_grid_spacing', name_type_map['Float'], (0, None), (False, 0.25), (lambda context: context.version >= 335806464, None)
		yield 'solver_iterations', name_type_map['Uint'], (0, None), (False, 5), (None, None)
		yield 'hier_solver_iterations', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 503382019, None)
		yield 'external_acceleration', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'wind_acceleration', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'wake_up_counter', name_type_map['Float'], (0, None), (False, 0.4), (None, None)
		yield 'sleep_linear_velocity', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'collision_group', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'collision_bits', Array, (0, None, (4,), name_type_map['Uint']), (False, None), (None, None)
		yield 'force_field_material', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'flags', name_type_map['NxClothFlag'], (0, None), (False, 32), (None, None)
		yield 'vertex_map_size', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 503447555, None)
		yield 'vertex_map', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (lambda context: context.version >= 503447555, None)
		yield 'num_states', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'states', Array, (0, None, (None,), name_type_map['PhysXClothState']), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'num_attachments', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'attachments', Array, (0, None, (None,), name_type_map['PhysXClothAttachment']), (False, None), (None, None)
		yield 'parent_actor', name_type_map['Ref'], (0, name_type_map['NiPhysXActorDesc']), (False, None), (None, None)
		yield 'dest', name_type_map['Ref'], (0, name_type_map['NiPhysXDest']), (False, None), (lambda context: context.version <= 335806473, None)
		yield 'target_mesh', name_type_map['Ref'], (0, name_type_map['NiMesh']), (False, None), (lambda context: 335872000 <= context.version <= 335872000, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'mesh', name_type_map['Ref'], (0, name_type_map['NiPhysXMeshDesc']), (False, None)
		if instance.context.version <= 335740937:
			yield 'pose', name_type_map['Matrix34'], (0, None), (False, None)
		yield 'thickness', name_type_map['Float'], (0, None), (False, 0.01)
		if instance.context.version >= 503382019:
			yield 'self_collision_thickness', name_type_map['Float'], (0, None), (False, None)
		yield 'density', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'bending_stiffness', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'stretching_stiffness', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'damping_coefficient', name_type_map['Float'], (0, None), (False, 0.5)
		if instance.context.version >= 503382019:
			yield 'hard_stretch_limitation_factor', name_type_map['Float'], (0, None), (False, None)
		yield 'friction', name_type_map['Float'], (0, None), (False, 0.5)
		yield 'pressure', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'tear_factor', name_type_map['Float'], (0, None), (False, 1.5)
		yield 'collision_response_coeff', name_type_map['Float'], (0, None), (False, 0.2)
		yield 'attach_response_coeff', name_type_map['Float'], (0, None), (False, 0.2)
		yield 'attach_tear_factor', name_type_map['Float'], (0, None), (False, 1.5)
		if instance.context.version >= 335806464:
			yield 'to_fluid_response_coeff', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'from_fluid_response_coeff', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'min_adhere_velocity', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'relative_grid_spacing', name_type_map['Float'], (0, None), (False, 0.25)
		yield 'solver_iterations', name_type_map['Uint'], (0, None), (False, 5)
		if instance.context.version >= 503382019:
			yield 'hier_solver_iterations', name_type_map['Uint'], (0, None), (False, None)
		yield 'external_acceleration', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version >= 335806464:
			yield 'wind_acceleration', name_type_map['Vector3'], (0, None), (False, None)
		yield 'wake_up_counter', name_type_map['Float'], (0, None), (False, 0.4)
		yield 'sleep_linear_velocity', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'collision_group', name_type_map['Ushort'], (0, None), (False, None)
		yield 'collision_bits', Array, (0, None, (4,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 335806464:
			yield 'force_field_material', name_type_map['Ushort'], (0, None), (False, None)
		yield 'flags', name_type_map['NxClothFlag'], (0, None), (False, 32)
		if instance.context.version >= 503447555:
			yield 'vertex_map_size', name_type_map['Ushort'], (0, None), (False, None)
			yield 'vertex_map', Array, (0, None, (instance.vertex_map_size,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 335806464:
			yield 'num_states', name_type_map['Uint'], (0, None), (False, None)
			yield 'states', Array, (0, None, (instance.num_states,), name_type_map['PhysXClothState']), (False, None)
		yield 'num_attachments', name_type_map['Uint'], (0, None), (False, None)
		yield 'attachments', Array, (0, None, (instance.num_attachments,), name_type_map['PhysXClothAttachment']), (False, None)
		yield 'parent_actor', name_type_map['Ref'], (0, name_type_map['NiPhysXActorDesc']), (False, None)
		if instance.context.version <= 335806473:
			yield 'dest', name_type_map['Ref'], (0, name_type_map['NiPhysXDest']), (False, None)
		if 335872000 <= instance.context.version <= 335872000:
			yield 'target_mesh', name_type_map['Ref'], (0, name_type_map['NiMesh']), (False, None)
