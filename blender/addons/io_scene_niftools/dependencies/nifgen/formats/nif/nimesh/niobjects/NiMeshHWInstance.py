from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class NiMeshHWInstance(NiAVObject):

	"""
	An instance of a hardware-instanced mesh in a scene graph.
	"""

	__name__ = 'NiMeshHWInstance'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The instanced mesh this object represents.
		self.master_mesh = name_type_map['Ref'](self.context, 0, name_type_map['NiMesh'])
		self.mesh_modifier = name_type_map['Ref'](self.context, 0, name_type_map['NiInstancingMeshModifier'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'master_mesh', name_type_map['Ref'], (0, name_type_map['NiMesh']), (False, None), (None, None)
		yield 'mesh_modifier', name_type_map['Ref'], (0, name_type_map['NiInstancingMeshModifier']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'master_mesh', name_type_map['Ref'], (0, name_type_map['NiMesh']), (False, None)
		yield 'mesh_modifier', name_type_map['Ref'], (0, name_type_map['NiInstancingMeshModifier']), (False, None)
