from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class Bone(BaseStruct):

	"""
	32 bytes
	bones, rot first
	"""

	__name__ = 'Bone'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.loc = name_type_map['Vector3'](self.context, 0, None)
		self.scale = name_type_map['Float'](self.context, 0, None)
		self.rot = name_type_map['Vector4'](self.context, 0, None)
		self.loc = name_type_map['Vector3'](self.context, 0, None)
		self.scale = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version <= 47, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 47, None)
		yield 'rot', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version <= 47, None)
		yield 'rot', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 48, None)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version >= 48, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 48, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 47:
			yield 'loc', name_type_map['Vector3'], (0, None), (False, None)
			yield 'scale', name_type_map['Float'], (0, None), (False, None)
			yield 'rot', name_type_map['Vector4'], (0, None), (False, None)
		if instance.context.version >= 48:
			yield 'rot', name_type_map['Vector4'], (0, None), (False, None)
			yield 'loc', name_type_map['Vector3'], (0, None), (False, None)
			yield 'scale', name_type_map['Float'], (0, None), (False, None)

	def set_bone(self, matrix):
		pos, quat, sca = matrix.decompose()
		self.loc.x, self.loc.y, self.loc.z = pos.x, pos.y, pos.z
		self.rot.x, self.rot.y, self.rot.z, self.rot.w = quat.x, quat.y, quat.z, quat.w
		self.scale = sca.x

