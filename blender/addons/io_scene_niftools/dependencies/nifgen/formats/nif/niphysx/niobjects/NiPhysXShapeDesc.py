from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXShapeDesc(NiObject):

	"""
	For serializing NxShapeDesc objects
	"""

	__name__ = 'NiPhysXShapeDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.shape_type = name_type_map['NxShapeType'](self.context, 0, None)
		self.local_pose = name_type_map['Matrix34'](self.context, 0, None)
		self.flags = name_type_map['NxShapeFlag'].from_value(1179656)
		self.collision_group = name_type_map['Ushort'](self.context, 0, None)
		self.material_index = name_type_map['Ushort'](self.context, 0, None)
		self.density = name_type_map['Float'].from_value(1.0)
		self.mass = name_type_map['Float'].from_value(-1.0)
		self.skin_width = name_type_map['Float'].from_value(-1.0)
		self.shape_name = name_type_map['NiFixedString'](self.context, 0, None)
		self.non_interacting_compartment_types = name_type_map['Uint'](self.context, 0, None)
		self.collision_bits = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.plane = name_type_map['NxPlane'](self.context, 0, None)
		self.sphere_radius = name_type_map['Float'](self.context, 0, None)
		self.box_half_extents = name_type_map['Vector3'](self.context, 0, None)
		self.capsule = name_type_map['NxCapsule'](self.context, 0, None)
		self.mesh = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXMeshDesc'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shape_type', name_type_map['NxShapeType'], (0, None), (False, None), (None, None)
		yield 'local_pose', name_type_map['Matrix34'], (0, None), (False, None), (None, None)
		yield 'flags', name_type_map['NxShapeFlag'], (0, None), (False, 1179656), (None, None)
		yield 'collision_group', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'material_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'density', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'skin_width', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'shape_name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'non_interacting_compartment_types', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'collision_bits', Array, (0, None, (4,), name_type_map['Uint']), (False, None), (None, None)
		yield 'plane', name_type_map['NxPlane'], (0, None), (False, None), (None, True)
		yield 'sphere_radius', name_type_map['Float'], (0, None), (False, None), (None, True)
		yield 'box_half_extents', name_type_map['Vector3'], (0, None), (False, None), (None, True)
		yield 'capsule', name_type_map['NxCapsule'], (0, None), (False, None), (None, True)
		yield 'mesh', name_type_map['Ref'], (0, name_type_map['NiPhysXMeshDesc']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shape_type', name_type_map['NxShapeType'], (0, None), (False, None)
		yield 'local_pose', name_type_map['Matrix34'], (0, None), (False, None)
		yield 'flags', name_type_map['NxShapeFlag'], (0, None), (False, 1179656)
		yield 'collision_group', name_type_map['Ushort'], (0, None), (False, None)
		yield 'material_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'density', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'mass', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'skin_width', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'shape_name', name_type_map['NiFixedString'], (0, None), (False, None)
		if instance.context.version >= 335806464:
			yield 'non_interacting_compartment_types', name_type_map['Uint'], (0, None), (False, None)
		yield 'collision_bits', Array, (0, None, (4,), name_type_map['Uint']), (False, None)
		if instance.shape_type == 0:
			yield 'plane', name_type_map['NxPlane'], (0, None), (False, None)
		if instance.shape_type == 1:
			yield 'sphere_radius', name_type_map['Float'], (0, None), (False, None)
		if instance.shape_type == 2:
			yield 'box_half_extents', name_type_map['Vector3'], (0, None), (False, None)
		if instance.shape_type == 3:
			yield 'capsule', name_type_map['NxCapsule'], (0, None), (False, None)
		if (instance.shape_type == 5) or (instance.shape_type == 6):
			yield 'mesh', name_type_map['Ref'], (0, name_type_map['NiPhysXMeshDesc']), (False, None)
