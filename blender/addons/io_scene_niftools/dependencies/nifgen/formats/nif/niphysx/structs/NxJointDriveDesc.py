from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NxJointDriveDesc(BaseStruct):

	__name__ = 'NxJointDriveDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.drive_type = name_type_map['NxD6JointDriveType'](self.context, 0, None)
		self.spring = name_type_map['Float'](self.context, 0, None)
		self.damping = name_type_map['Float'](self.context, 0, None)
		self.force_limit = name_type_map['Float'].from_value(3.402823466e+38)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'drive_type', name_type_map['NxD6JointDriveType'], (0, None), (False, None), (None, None)
		yield 'spring', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'force_limit', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'drive_type', name_type_map['NxD6JointDriveType'], (0, None), (False, None)
		yield 'spring', name_type_map['Float'], (0, None), (False, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, None)
		yield 'force_limit', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
