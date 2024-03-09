from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimesh.niobjects.NiMeshModifier import NiMeshModifier


class NiInstancingMeshModifier(NiMeshModifier):

	"""
	Mesh modifier that provides per-frame instancing capabilities in Gamebryo.
	"""

	__name__ = 'NiInstancingMeshModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.has_instance_nodes = name_type_map['Bool'](self.context, 0, None)
		self.per_instance_culling = name_type_map['Bool'](self.context, 0, None)
		self.has_static_bounds = name_type_map['Bool'](self.context, 0, None)
		self.affected_mesh = name_type_map['Ref'](self.context, 0, name_type_map['NiMesh'])
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)
		self.num_instance_nodes = name_type_map['Uint'](self.context, 0, None)
		self.instance_nodes = Array(self.context, 0, name_type_map['NiMeshHWInstance'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_instance_nodes', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'per_instance_culling', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'has_static_bounds', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'affected_mesh', name_type_map['Ref'], (0, name_type_map['NiMesh']), (False, None), (None, None)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, True)
		yield 'num_instance_nodes', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'instance_nodes', Array, (0, name_type_map['NiMeshHWInstance'], (None,), name_type_map['Ref']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_instance_nodes', name_type_map['Bool'], (0, None), (False, None)
		yield 'per_instance_culling', name_type_map['Bool'], (0, None), (False, None)
		yield 'has_static_bounds', name_type_map['Bool'], (0, None), (False, None)
		yield 'affected_mesh', name_type_map['Ref'], (0, name_type_map['NiMesh']), (False, None)
		if instance.has_static_bounds:
			yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		if instance.has_instance_nodes:
			yield 'num_instance_nodes', name_type_map['Uint'], (0, None), (False, None)
			yield 'instance_nodes', Array, (0, name_type_map['NiMeshHWInstance'], (instance.num_instance_nodes,), name_type_map['Ref']), (False, None)
