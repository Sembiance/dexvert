from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiPhysXJointLimit(BaseStruct):

	__name__ = 'NiPhysXJointLimit'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.limit_plane_normal = name_type_map['Vector3'](self.context, 0, None)
		self.limit_plane_d = name_type_map['Float'](self.context, 0, None)
		self.limit_plane_r = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'limit_plane_normal', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'limit_plane_d', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'limit_plane_r', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335806464, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'limit_plane_normal', name_type_map['Vector3'], (0, None), (False, None)
		yield 'limit_plane_d', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335806464:
			yield 'limit_plane_r', name_type_map['Float'], (0, None), (False, None)
