from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiRotData(NiObject):

	"""
	Wrapper for rotation animation keys.
	"""

	__name__ = 'NiRotData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_rotation_keys = name_type_map['Uint'](self.context, 0, None)
		self.rotation_type = name_type_map['KeyType'](self.context, 0, None)
		self.quaternion_keys = Array(self.context, self.rotation_type, name_type_map['Quaternion'], (0,), name_type_map['QuatKey'])
		self.xyz_rotations = Array(self.context, 0, name_type_map['Float'], (0,), name_type_map['KeyGroup'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_rotation_keys', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'rotation_type', name_type_map['KeyType'], (0, None), (False, None), (None, True)
		yield 'quaternion_keys', Array, (None, name_type_map['Quaternion'], (None,), name_type_map['QuatKey']), (False, None), (None, True)
		yield 'xyz_rotations', Array, (0, name_type_map['Float'], (3,), name_type_map['KeyGroup']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_rotation_keys', name_type_map['Uint'], (0, None), (False, None)
		if instance.num_rotation_keys != 0:
			yield 'rotation_type', name_type_map['KeyType'], (0, None), (False, None)
		if instance.rotation_type != 4:
			yield 'quaternion_keys', Array, (instance.rotation_type, name_type_map['Quaternion'], (instance.num_rotation_keys,), name_type_map['QuatKey']), (False, None)
		if instance.rotation_type == 4:
			yield 'xyz_rotations', Array, (0, name_type_map['Float'], (3,), name_type_map['KeyGroup']), (False, None)
