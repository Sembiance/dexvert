from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXSceneDesc(NiObject):

	"""
	Object which caches the properties of NxScene, stored as a snapshot in a NiPhysXScene.
	"""

	__name__ = 'NiPhysXSceneDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.broad_phase_type = name_type_map['NiSceneDescNxBroadPhaseType'](self.context, 0, None)
		self.gravity = name_type_map['Vector3'](self.context, 0, None)
		self.max_timestep = name_type_map['Float'].from_value(0.016666)
		self.max_iterations = name_type_map['Uint'].from_value(8)
		self.time_step_method = name_type_map['NxTimeStepMethod'].TIMESTEP_FIXED
		self.has_bound = name_type_map['Bool'](self.context, 0, None)
		self.max_bounds_min = name_type_map['Vector3'](self.context, 0, None)
		self.max_bounds_max = name_type_map['Vector3'](self.context, 0, None)
		self.has_limits = name_type_map['Bool'](self.context, 0, None)
		self.max_actors = name_type_map['Uint'](self.context, 0, None)
		self.max_bodies = name_type_map['Uint'](self.context, 0, None)
		self.max_static_shapes = name_type_map['Uint'](self.context, 0, None)
		self.max_dynamic_shapes = name_type_map['Uint'](self.context, 0, None)
		self.simulation_type = name_type_map['NxSimulationType'].SIMULATION_SW
		self.hw_scene_type = name_type_map['NiSceneDescNxHwSceneType'](self.context, 0, None)
		self.hw_pipeline_spec = name_type_map['NiSceneDescNxHwPipelineSpec'](self.context, 0, None)
		self.ground_plane = name_type_map['Bool'](self.context, 0, None)
		self.bounds_plane = name_type_map['Bool'](self.context, 0, None)
		self.collision_detection = name_type_map['Bool'](self.context, 0, None)
		self.flags = name_type_map['Uint'](self.context, 0, None)
		self.internal_thread_count = name_type_map['Uint'](self.context, 0, None)
		self.background_thread_count = name_type_map['Uint'](self.context, 0, None)
		self.thread_mask = name_type_map['Uint'](self.context, 0, None)
		self.background_thread_priority = name_type_map['Uint'](self.context, 0, None)
		self.background_thread_mask = name_type_map['Uint'](self.context, 0, None)
		self.num_hw_scenes = name_type_map['Uint'](self.context, 0, None)
		self.sim_thread_stack_size = name_type_map['Uint'](self.context, 0, None)
		self.sim_thread_priority = name_type_map['NxThreadPriority'].TP_NORMAL
		self.worker_thread_stack_size = name_type_map['Uint'](self.context, 0, None)
		self.worker_thread_priority = name_type_map['NxThreadPriority'].TP_NORMAL
		self.up_axis = name_type_map['Uint'](self.context, 0, None)
		self.subdivision_level = name_type_map['Uint'].from_value(5)
		self.static_structure = name_type_map['NxPruningStructure'].PRUNING_NONE
		self.dynamic_structure = name_type_map['NxPruningStructure'].PRUNING_STATIC_AABB_TREE
		self.dynamic_tree_rebuild_rate_hint = name_type_map['Uint'](self.context, 0, None)
		self.broad_phase_type = name_type_map['NxBroadPhaseType'](self.context, 0, None)
		self.grid_cells_x = name_type_map['Uint'](self.context, 0, None)
		self.grid_cells_y = name_type_map['Uint'](self.context, 0, None)
		self.num_actors = name_type_map['Uint'](self.context, 0, None)
		self.actors = Array(self.context, 0, name_type_map['NiPhysXActorDesc'], (0,), name_type_map['Ref'])
		self.num_joints = name_type_map['Uint'](self.context, 0, None)
		self.joints = Array(self.context, 0, name_type_map['NiPhysXJointDesc'], (0,), name_type_map['Ref'])
		self.num_materials = name_type_map['Uint'](self.context, 0, None)
		self.materials = Array(self.context, 0, None, (0,), name_type_map['NiPhysXMaterialDescMap'])
		self.group_collision_flags = Array(self.context, 0, None, (0,), name_type_map['Bool'])
		self.filter_ops = Array(self.context, 0, None, (0,), name_type_map['NxFilterOp'])
		self.filter_constants = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.filter = name_type_map['Bool'].from_value(True)
		self.num_states = name_type_map['Uint'](self.context, 0, None)
		self.num_compartments = name_type_map['Uint'](self.context, 0, None)
		self.compartments = Array(self.context, 0, None, (0,), name_type_map['NxCompartmentDescMap'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'broad_phase_type', name_type_map['NiSceneDescNxBroadPhaseType'], (0, None), (False, None), (lambda context: context.version <= 335675399, None)
		yield 'gravity', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'max_timestep', name_type_map['Float'], (0, None), (False, 0.016666), (None, None)
		yield 'max_iterations', name_type_map['Uint'], (0, None), (False, 8), (None, None)
		yield 'time_step_method', name_type_map['NxTimeStepMethod'], (0, None), (False, name_type_map['NxTimeStepMethod'].TIMESTEP_FIXED), (None, None)
		yield 'has_bound', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'max_bounds_min', name_type_map['Vector3'], (0, None), (False, None), (None, True)
		yield 'max_bounds_max', name_type_map['Vector3'], (0, None), (False, None), (None, True)
		yield 'has_limits', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'max_actors', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'max_bodies', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'max_static_shapes', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'max_dynamic_shapes', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'simulation_type', name_type_map['NxSimulationType'], (0, None), (False, name_type_map['NxSimulationType'].SIMULATION_SW), (None, None)
		yield 'hw_scene_type', name_type_map['NiSceneDescNxHwSceneType'], (0, None), (False, None), (lambda context: context.version <= 335675400, None)
		yield 'hw_pipeline_spec', name_type_map['NiSceneDescNxHwPipelineSpec'], (0, None), (False, None), (lambda context: context.version <= 335675400, None)
		yield 'ground_plane', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'bounds_plane', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'collision_detection', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 335675399, None)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335675400, None)
		yield 'internal_thread_count', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335675400, None)
		yield 'background_thread_count', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335675400, None)
		yield 'thread_mask', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335675400, None)
		yield 'background_thread_priority', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335872003, None)
		yield 'background_thread_mask', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335675400, None)
		yield 'num_hw_scenes', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335740929 <= context.version <= 335740933, None)
		yield 'sim_thread_stack_size', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335740929, None)
		yield 'sim_thread_priority', name_type_map['NxThreadPriority'], (0, None), (False, name_type_map['NxThreadPriority'].TP_NORMAL), (lambda context: context.version >= 335740929, None)
		yield 'worker_thread_stack_size', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335740929, None)
		yield 'worker_thread_priority', name_type_map['NxThreadPriority'], (0, None), (False, name_type_map['NxThreadPriority'].TP_NORMAL), (lambda context: context.version >= 335740929, None)
		yield 'up_axis', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335740929, None)
		yield 'subdivision_level', name_type_map['Uint'], (0, None), (False, 5), (lambda context: context.version >= 335740929, None)
		yield 'static_structure', name_type_map['NxPruningStructure'], (0, None), (False, name_type_map['NxPruningStructure'].PRUNING_NONE), (lambda context: context.version >= 335740929, None)
		yield 'dynamic_structure', name_type_map['NxPruningStructure'], (0, None), (False, name_type_map['NxPruningStructure'].PRUNING_STATIC_AABB_TREE), (lambda context: context.version >= 335740929, None)
		yield 'dynamic_tree_rebuild_rate_hint', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335872003, None)
		yield 'broad_phase_type', name_type_map['NxBroadPhaseType'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'grid_cells_x', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'grid_cells_y', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'num_actors', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 335740929, None)
		yield 'actors', Array, (0, name_type_map['NiPhysXActorDesc'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version <= 335740929, None)
		yield 'num_joints', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 335740929, None)
		yield 'joints', Array, (0, name_type_map['NiPhysXJointDesc'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version <= 335740929, None)
		yield 'num_materials', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 335740929, None)
		yield 'materials', Array, (0, None, (None,), name_type_map['NiPhysXMaterialDescMap']), (False, None), (lambda context: context.version <= 335740929, None)
		yield 'group_collision_flags', Array, (0, None, (1024,), name_type_map['Bool']), (False, None), (None, None)
		yield 'filter_ops', Array, (0, None, (3,), name_type_map['NxFilterOp']), (False, None), (None, None)
		yield 'filter_constants', Array, (0, None, (8,), name_type_map['Uint']), (False, None), (None, None)
		yield 'filter', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'num_states', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 335740929, None)
		yield 'num_compartments', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335740934, None)
		yield 'compartments', Array, (0, None, (None,), name_type_map['NxCompartmentDescMap']), (False, None), (lambda context: context.version >= 335740934, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 335675399:
			yield 'broad_phase_type', name_type_map['NiSceneDescNxBroadPhaseType'], (0, None), (False, None)
		yield 'gravity', name_type_map['Vector3'], (0, None), (False, None)
		yield 'max_timestep', name_type_map['Float'], (0, None), (False, 0.016666)
		yield 'max_iterations', name_type_map['Uint'], (0, None), (False, 8)
		yield 'time_step_method', name_type_map['NxTimeStepMethod'], (0, None), (False, name_type_map['NxTimeStepMethod'].TIMESTEP_FIXED)
		yield 'has_bound', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_bound:
			yield 'max_bounds_min', name_type_map['Vector3'], (0, None), (False, None)
			yield 'max_bounds_max', name_type_map['Vector3'], (0, None), (False, None)
		yield 'has_limits', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_limits:
			yield 'max_actors', name_type_map['Uint'], (0, None), (False, None)
			yield 'max_bodies', name_type_map['Uint'], (0, None), (False, None)
			yield 'max_static_shapes', name_type_map['Uint'], (0, None), (False, None)
			yield 'max_dynamic_shapes', name_type_map['Uint'], (0, None), (False, None)
		yield 'simulation_type', name_type_map['NxSimulationType'], (0, None), (False, name_type_map['NxSimulationType'].SIMULATION_SW)
		if instance.context.version <= 335675400:
			yield 'hw_scene_type', name_type_map['NiSceneDescNxHwSceneType'], (0, None), (False, None)
			yield 'hw_pipeline_spec', name_type_map['NiSceneDescNxHwPipelineSpec'], (0, None), (False, None)
		yield 'ground_plane', name_type_map['Bool'], (0, None), (False, None)
		yield 'bounds_plane', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 335675399:
			yield 'collision_detection', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335675400:
			yield 'flags', name_type_map['Uint'], (0, None), (False, None)
			yield 'internal_thread_count', name_type_map['Uint'], (0, None), (False, None)
			yield 'background_thread_count', name_type_map['Uint'], (0, None), (False, None)
			yield 'thread_mask', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335872003:
			yield 'background_thread_priority', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335675400:
			yield 'background_thread_mask', name_type_map['Uint'], (0, None), (False, None)
		if 335740929 <= instance.context.version <= 335740933:
			yield 'num_hw_scenes', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335740929:
			yield 'sim_thread_stack_size', name_type_map['Uint'], (0, None), (False, None)
			yield 'sim_thread_priority', name_type_map['NxThreadPriority'], (0, None), (False, name_type_map['NxThreadPriority'].TP_NORMAL)
			yield 'worker_thread_stack_size', name_type_map['Uint'], (0, None), (False, None)
			yield 'worker_thread_priority', name_type_map['NxThreadPriority'], (0, None), (False, name_type_map['NxThreadPriority'].TP_NORMAL)
			yield 'up_axis', name_type_map['Uint'], (0, None), (False, None)
			yield 'subdivision_level', name_type_map['Uint'], (0, None), (False, 5)
			yield 'static_structure', name_type_map['NxPruningStructure'], (0, None), (False, name_type_map['NxPruningStructure'].PRUNING_NONE)
			yield 'dynamic_structure', name_type_map['NxPruningStructure'], (0, None), (False, name_type_map['NxPruningStructure'].PRUNING_STATIC_AABB_TREE)
		if instance.context.version >= 335872003:
			yield 'dynamic_tree_rebuild_rate_hint', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335806464:
			yield 'broad_phase_type', name_type_map['NxBroadPhaseType'], (0, None), (False, None)
			yield 'grid_cells_x', name_type_map['Uint'], (0, None), (False, None)
			yield 'grid_cells_y', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 335740929:
			yield 'num_actors', name_type_map['Uint'], (0, None), (False, None)
			yield 'actors', Array, (0, name_type_map['NiPhysXActorDesc'], (instance.num_actors,), name_type_map['Ref']), (False, None)
			yield 'num_joints', name_type_map['Uint'], (0, None), (False, None)
			yield 'joints', Array, (0, name_type_map['NiPhysXJointDesc'], (instance.num_joints,), name_type_map['Ref']), (False, None)
			yield 'num_materials', name_type_map['Uint'], (0, None), (False, None)
			yield 'materials', Array, (0, None, (instance.num_materials,), name_type_map['NiPhysXMaterialDescMap']), (False, None)
		yield 'group_collision_flags', Array, (0, None, (1024,), name_type_map['Bool']), (False, None)
		yield 'filter_ops', Array, (0, None, (3,), name_type_map['NxFilterOp']), (False, None)
		yield 'filter_constants', Array, (0, None, (8,), name_type_map['Uint']), (False, None)
		yield 'filter', name_type_map['Bool'], (0, None), (False, True)
		if instance.context.version <= 335740929:
			yield 'num_states', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335740934:
			yield 'num_compartments', name_type_map['Uint'], (0, None), (False, None)
			yield 'compartments', Array, (0, None, (instance.num_compartments,), name_type_map['NxCompartmentDescMap']), (False, None)
