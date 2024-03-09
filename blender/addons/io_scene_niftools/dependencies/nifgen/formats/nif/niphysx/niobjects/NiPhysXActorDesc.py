from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXActorDesc(NiObject):

	"""
	For serializing NxActor objects.
	"""

	__name__ = 'NiPhysXActorDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.actor_name = name_type_map['NiFixedString'](self.context, 0, None)
		self.num_poses = name_type_map['Uint'](self.context, 0, None)
		self.poses = Array(self.context, 0, None, (0,), name_type_map['Matrix34'])
		self.body_desc = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXBodyDesc'])
		self.density = name_type_map['Float'](self.context, 0, None)
		self.actor_flags = name_type_map['Uint'](self.context, 0, None)
		self.actor_group = name_type_map['Ushort'](self.context, 0, None)
		self.dominance_group = name_type_map['Ushort'](self.context, 0, None)
		self.contact_report_flags = name_type_map['Uint'](self.context, 0, None)
		self.force_field_material = name_type_map['Ushort'](self.context, 0, None)
		self.dummy = name_type_map['Uint'](self.context, 0, None)
		self.num_shape_descs = name_type_map['Uint'](self.context, 0, None)
		self.shape_descriptions = Array(self.context, 0, name_type_map['NiPhysXShapeDesc'], (0,), name_type_map['Ref'])
		self.actor_parent = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXActorDesc'])
		self.source = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXRigidBodySrc'])
		self.dest = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXRigidBodyDest'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'actor_name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'num_poses', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'poses', Array, (0, None, (None,), name_type_map['Matrix34']), (False, None), (None, None)
		yield 'body_desc', name_type_map['Ref'], (0, name_type_map['NiPhysXBodyDesc']), (False, None), (None, None)
		yield 'density', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'actor_flags', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'actor_group', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'dominance_group', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'contact_report_flags', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'force_field_material', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)
		yield 'dummy', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335740929 <= context.version <= 335740933, None)
		yield 'num_shape_descs', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'shape_descriptions', Array, (0, name_type_map['NiPhysXShapeDesc'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'actor_parent', name_type_map['Ref'], (0, name_type_map['NiPhysXActorDesc']), (False, None), (None, None)
		yield 'source', name_type_map['Ref'], (0, name_type_map['NiPhysXRigidBodySrc']), (False, None), (None, None)
		yield 'dest', name_type_map['Ref'], (0, name_type_map['NiPhysXRigidBodyDest']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'actor_name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'num_poses', name_type_map['Uint'], (0, None), (False, None)
		yield 'poses', Array, (0, None, (instance.num_poses,), name_type_map['Matrix34']), (False, None)
		yield 'body_desc', name_type_map['Ref'], (0, name_type_map['NiPhysXBodyDesc']), (False, None)
		yield 'density', name_type_map['Float'], (0, None), (False, None)
		yield 'actor_flags', name_type_map['Uint'], (0, None), (False, None)
		yield 'actor_group', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 335806464:
			yield 'dominance_group', name_type_map['Ushort'], (0, None), (False, None)
			yield 'contact_report_flags', name_type_map['Uint'], (0, None), (False, None)
			yield 'force_field_material', name_type_map['Ushort'], (0, None), (False, None)
		if 335740929 <= instance.context.version <= 335740933:
			yield 'dummy', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_shape_descs', name_type_map['Uint'], (0, None), (False, None)
		yield 'shape_descriptions', Array, (0, name_type_map['NiPhysXShapeDesc'], (instance.num_shape_descs,), name_type_map['Ref']), (False, None)
		yield 'actor_parent', name_type_map['Ref'], (0, name_type_map['NiPhysXActorDesc']), (False, None)
		yield 'source', name_type_map['Ref'], (0, name_type_map['NiPhysXRigidBodySrc']), (False, None)
		yield 'dest', name_type_map['Ref'], (0, name_type_map['NiPhysXRigidBodyDest']), (False, None)
