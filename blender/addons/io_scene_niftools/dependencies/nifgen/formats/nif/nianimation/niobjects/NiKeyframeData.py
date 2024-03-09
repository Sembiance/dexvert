from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiKeyframeData(NiObject):

	"""
	DEPRECATED (10.2), RENAMED (10.2) to NiTransformData.
	Wrapper for transformation animation keys.
	"""

	__name__ = 'NiKeyframeData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The number of quaternion rotation keys. If the rotation type is XYZ (type 4) then this *must* be set to 1, and in this case the actual number of keys is stored in the XYZ Rotations field.
		self.num_rotation_keys = name_type_map['Uint'](self.context, 0, None)

		# The type of interpolation to use for rotation.  Can also be 4 to indicate that separate X, Y, and Z values are used for the rotation instead of Quaternions.
		self.rotation_type = name_type_map['KeyType'](self.context, 0, None)

		# The rotation keys if Quaternion rotation is used.
		self.quaternion_keys = Array(self.context, self.rotation_type, name_type_map['Quaternion'], (0,), name_type_map['QuatKey'])
		self.order = name_type_map['Float'](self.context, 0, None)

		# Individual arrays of keys for rotating X, Y, and Z individually.
		self.xyz_rotations = Array(self.context, 0, name_type_map['Float'], (0,), name_type_map['KeyGroup'])

		# Translation keys.
		self.translations = name_type_map['KeyGroup'](self.context, 0, name_type_map['Vector3'])

		# Scale keys.
		self.scales = name_type_map['KeyGroup'](self.context, 0, name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_rotation_keys', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'rotation_type', name_type_map['KeyType'], (0, None), (False, None), (None, True)
		yield 'quaternion_keys', Array, (None, name_type_map['Quaternion'], (None,), name_type_map['QuatKey']), (False, None), (None, True)
		yield 'order', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 167837696, True)
		yield 'xyz_rotations', Array, (0, name_type_map['Float'], (3,), name_type_map['KeyGroup']), (False, None), (None, True)
		yield 'translations', name_type_map['KeyGroup'], (0, name_type_map['Vector3']), (False, None), (None, None)
		yield 'scales', name_type_map['KeyGroup'], (0, name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_rotation_keys', name_type_map['Uint'], (0, None), (False, None)
		if instance.num_rotation_keys != 0:
			yield 'rotation_type', name_type_map['KeyType'], (0, None), (False, None)
		if instance.rotation_type != 4:
			yield 'quaternion_keys', Array, (instance.rotation_type, name_type_map['Quaternion'], (instance.num_rotation_keys,), name_type_map['QuatKey']), (False, None)
		if instance.context.version <= 167837696 and instance.rotation_type == 4:
			yield 'order', name_type_map['Float'], (0, None), (False, None)
		if instance.rotation_type == 4:
			yield 'xyz_rotations', Array, (0, name_type_map['Float'], (3,), name_type_map['KeyGroup']), (False, None)
		yield 'translations', name_type_map['KeyGroup'], (0, name_type_map['Vector3']), (False, None)
		yield 'scales', name_type_map['KeyGroup'], (0, name_type_map['Float']), (False, None)
	def apply_scale(self, scale):
		"""Apply scale factor on data."""
		super().apply_scale(scale)
		for key in self.translations.keys:
			key.value.x *= scale
			key.value.y *= scale
			key.value.z *= scale
			#key.forward.x *= scale
			#key.forward.y *= scale
			#key.forward.z *= scale
			#key.backward.x *= scale
			#key.backward.y *= scale
			#key.backward.z *= scale
			# what to do with TBC?


