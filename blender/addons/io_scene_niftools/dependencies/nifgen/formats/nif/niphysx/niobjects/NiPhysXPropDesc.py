from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXPropDesc(NiObject):

	"""
	For serialization of PhysX objects and to attach them to the scene.
	"""

	__name__ = 'NiPhysXPropDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_actors = name_type_map['Uint'](self.context, 0, None)
		self.actors = Array(self.context, 0, name_type_map['NiPhysXActorDesc'], (0,), name_type_map['Ref'])
		self.num_joints = name_type_map['Uint'](self.context, 0, None)
		self.joints = Array(self.context, 0, name_type_map['NiPhysXJointDesc'], (0,), name_type_map['Ref'])
		self.num_clothes = name_type_map['Uint'](self.context, 0, None)
		self.clothes = Array(self.context, 0, name_type_map['NiPhysXClothDesc'], (0,), name_type_map['Ref'])
		self.num_materials = name_type_map['Uint'](self.context, 0, None)
		self.materials = Array(self.context, 0, None, (0,), name_type_map['NiPhysXMaterialDescMap'])
		self.num_states = name_type_map['Uint'](self.context, 0, None)
		self.state_names = name_type_map['NiTFixedStringMap'](self.context, 0, name_type_map['Uint'])
		self.flags = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_actors', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'actors', Array, (0, name_type_map['NiPhysXActorDesc'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_joints', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'joints', Array, (0, name_type_map['NiPhysXJointDesc'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_clothes', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335740933, None)
		yield 'clothes', Array, (0, name_type_map['NiPhysXClothDesc'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 335740933, None)
		yield 'num_materials', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'materials', Array, (0, None, (None,), name_type_map['NiPhysXMaterialDescMap']), (False, None), (None, None)
		yield 'num_states', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'state_names', name_type_map['NiTFixedStringMap'], (0, name_type_map['Uint']), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'flags', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_actors', name_type_map['Uint'], (0, None), (False, None)
		yield 'actors', Array, (0, name_type_map['NiPhysXActorDesc'], (instance.num_actors,), name_type_map['Ref']), (False, None)
		yield 'num_joints', name_type_map['Uint'], (0, None), (False, None)
		yield 'joints', Array, (0, name_type_map['NiPhysXJointDesc'], (instance.num_joints,), name_type_map['Ref']), (False, None)
		if instance.context.version >= 335740933:
			yield 'num_clothes', name_type_map['Uint'], (0, None), (False, None)
			yield 'clothes', Array, (0, name_type_map['NiPhysXClothDesc'], (instance.num_clothes,), name_type_map['Ref']), (False, None)
		yield 'num_materials', name_type_map['Uint'], (0, None), (False, None)
		yield 'materials', Array, (0, None, (instance.num_materials,), name_type_map['NiPhysXMaterialDescMap']), (False, None)
		yield 'num_states', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335806464:
			yield 'state_names', name_type_map['NiTFixedStringMap'], (0, name_type_map['Uint']), (False, None)
			yield 'flags', name_type_map['Byte'], (0, None), (False, None)
