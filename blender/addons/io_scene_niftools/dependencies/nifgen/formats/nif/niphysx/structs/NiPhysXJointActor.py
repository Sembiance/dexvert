from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiPhysXJointActor(BaseStruct):

	__name__ = 'NiPhysXJointActor'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.actor = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXActorDesc'])
		self.local_normal = name_type_map['Vector3'](self.context, 0, None)
		self.local_axis = name_type_map['Vector3'](self.context, 0, None)
		self.local_anchor = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'actor', name_type_map['Ref'], (0, name_type_map['NiPhysXActorDesc']), (False, None), (None, None)
		yield 'local_normal', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'local_axis', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'local_anchor', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'actor', name_type_map['Ref'], (0, name_type_map['NiPhysXActorDesc']), (False, None)
		yield 'local_normal', name_type_map['Vector3'], (0, None), (False, None)
		yield 'local_axis', name_type_map['Vector3'], (0, None), (False, None)
		yield 'local_anchor', name_type_map['Vector3'], (0, None), (False, None)
