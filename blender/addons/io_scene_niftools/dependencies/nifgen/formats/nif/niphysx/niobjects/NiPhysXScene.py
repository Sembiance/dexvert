from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObjectNET import NiObjectNET


class NiPhysXScene(NiObjectNET):

	"""
	Object which manages a NxScene object and the Gamebryo objects that interact with it.
	"""

	__name__ = 'NiPhysXScene'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.scene_transform = name_type_map['NiTransform'](self.context, 0, None)
		self.phys_x_to_world_scale = name_type_map['Float'].from_value(1.0)
		self.num_props = name_type_map['Uint'](self.context, 0, None)
		self.props = Array(self.context, 0, name_type_map['NiPhysXProp'], (0,), name_type_map['Ref'])
		self.num_sources = name_type_map['Uint'](self.context, 0, None)
		self.sources = Array(self.context, 0, name_type_map['NiPhysXSrc'], (0,), name_type_map['Ref'])
		self.num_dests = name_type_map['Uint'](self.context, 0, None)
		self.dests = Array(self.context, 0, name_type_map['NiPhysXDest'], (0,), name_type_map['Ref'])
		self.num_modified_meshes = name_type_map['Uint'](self.context, 0, None)
		self.modified_meshes = Array(self.context, 0, name_type_map['NiMesh'], (0,), name_type_map['Ref'])
		self.time_step = name_type_map['Float'].from_value(0.016666)
		self.keep_meshes = name_type_map['Bool'](self.context, 0, None)
		self.num_sub_steps = name_type_map['Uint'].from_value(1)
		self.max_sub_steps = name_type_map['Uint'].from_value(8)
		self.snapshot = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXSceneDesc'])
		self.flags = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'scene_transform', name_type_map['NiTransform'], (0, None), (False, None), (None, None)
		yield 'phys_x_to_world_scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'num_props', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335740930, None)
		yield 'props', Array, (0, name_type_map['NiPhysXProp'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 335740930, None)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'sources', Array, (0, name_type_map['NiPhysXSrc'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_dests', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'dests', Array, (0, name_type_map['NiPhysXDest'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_modified_meshes', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'modified_meshes', Array, (0, name_type_map['NiMesh'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'time_step', name_type_map['Float'], (0, None), (False, 0.016666), (lambda context: context.version >= 335675400, None)
		yield 'keep_meshes', name_type_map['Bool'], (0, None), (False, None), (lambda context: 335675400 <= context.version <= 335740929, None)
		yield 'num_sub_steps', name_type_map['Uint'], (0, None), (False, 1), (lambda context: context.version >= 335740937, None)
		yield 'max_sub_steps', name_type_map['Uint'], (0, None), (False, 8), (lambda context: context.version >= 335740937, None)
		yield 'snapshot', name_type_map['Ref'], (0, name_type_map['NiPhysXSceneDesc']), (False, None), (None, None)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'scene_transform', name_type_map['NiTransform'], (0, None), (False, None)
		yield 'phys_x_to_world_scale', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.version >= 335740930:
			yield 'num_props', name_type_map['Uint'], (0, None), (False, None)
			yield 'props', Array, (0, name_type_map['NiPhysXProp'], (instance.num_props,), name_type_map['Ref']), (False, None)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None)
		yield 'sources', Array, (0, name_type_map['NiPhysXSrc'], (instance.num_sources,), name_type_map['Ref']), (False, None)
		yield 'num_dests', name_type_map['Uint'], (0, None), (False, None)
		yield 'dests', Array, (0, name_type_map['NiPhysXDest'], (instance.num_dests,), name_type_map['Ref']), (False, None)
		if instance.context.version >= 335806464:
			yield 'num_modified_meshes', name_type_map['Uint'], (0, None), (False, None)
			yield 'modified_meshes', Array, (0, name_type_map['NiMesh'], (instance.num_modified_meshes,), name_type_map['Ref']), (False, None)
		if instance.context.version >= 335675400:
			yield 'time_step', name_type_map['Float'], (0, None), (False, 0.016666)
		if 335675400 <= instance.context.version <= 335740929:
			yield 'keep_meshes', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 335740937:
			yield 'num_sub_steps', name_type_map['Uint'], (0, None), (False, 1)
			yield 'max_sub_steps', name_type_map['Uint'], (0, None), (False, 8)
		yield 'snapshot', name_type_map['Ref'], (0, name_type_map['NiPhysXSceneDesc']), (False, None)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
