from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObjectNET import NiObjectNET


class NiPhysXProp(NiObjectNET):

	"""
	A PhysX prop which holds information about PhysX actors in a Gamebryo scene
	"""

	__name__ = 'NiPhysXProp'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.phys_x_to_world_scale = name_type_map['Float'].from_value(1.0)
		self.num_sources = name_type_map['Uint'](self.context, 0, None)
		self.sources = Array(self.context, 0, name_type_map['NiPhysXSrc'], (0,), name_type_map['Ref'])
		self.num_dests = name_type_map['Uint'](self.context, 0, None)
		self.dests = Array(self.context, 0, name_type_map['NiPhysXDest'], (0,), name_type_map['Ref'])
		self.num_modified_meshes = name_type_map['Uint'](self.context, 0, None)
		self.modified_meshes = Array(self.context, 0, name_type_map['NiMesh'], (0,), name_type_map['Ref'])
		self.temp_name = name_type_map['NiFixedString'](self.context, 0, None)
		self.keep_meshes = name_type_map['Bool'](self.context, 0, None)
		self.snapshot = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXPropDesc'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'phys_x_to_world_scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'sources', Array, (0, name_type_map['NiPhysXSrc'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_dests', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'dests', Array, (0, name_type_map['NiPhysXDest'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_modified_meshes', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'modified_meshes', Array, (0, name_type_map['NiMesh'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'temp_name', name_type_map['NiFixedString'], (0, None), (False, None), (lambda context: 503382018 <= context.version <= 503447554, None)
		yield 'keep_meshes', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'snapshot', name_type_map['Ref'], (0, name_type_map['NiPhysXPropDesc']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'phys_x_to_world_scale', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None)
		yield 'sources', Array, (0, name_type_map['NiPhysXSrc'], (instance.num_sources,), name_type_map['Ref']), (False, None)
		yield 'num_dests', name_type_map['Uint'], (0, None), (False, None)
		yield 'dests', Array, (0, name_type_map['NiPhysXDest'], (instance.num_dests,), name_type_map['Ref']), (False, None)
		if instance.context.version >= 335806464:
			yield 'num_modified_meshes', name_type_map['Uint'], (0, None), (False, None)
			yield 'modified_meshes', Array, (0, name_type_map['NiMesh'], (instance.num_modified_meshes,), name_type_map['Ref']), (False, None)
		if 503382018 <= instance.context.version <= 503447554:
			yield 'temp_name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'keep_meshes', name_type_map['Bool'], (0, None), (False, None)
		yield 'snapshot', name_type_map['Ref'], (0, name_type_map['NiPhysXPropDesc']), (False, None)
