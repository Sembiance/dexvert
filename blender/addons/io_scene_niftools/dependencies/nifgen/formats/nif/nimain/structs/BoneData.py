from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BoneData(BaseStruct):

	"""
	NiSkinData::BoneData. Skinning data component.
	"""

	__name__ = 'BoneData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Offset of the skin from this bone in bind position.
		self.skin_transform = name_type_map['NiTransform'](self.context, 0, None)

		# Note that its a Sphere Containing Axis Aligned Box not a minimum volume Sphere
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)

		# Number of weighted vertices.
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)

		# The vertex weights.
		self.vertex_weights = Array(self.context, 0, None, (0,), name_type_map['BoneVertDataHalf'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'skin_transform', name_type_map['NiTransform'], (0, None), (False, None), (None, None)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'vertex_weights', Array, (0, None, (None,), name_type_map['BoneVertData']), (False, None), (lambda context: context.version <= 67240192, None)
		yield 'vertex_weights', Array, (0, None, (None,), name_type_map['BoneVertData']), (False, None), (lambda context: context.version >= 67240448, True)
		yield 'vertex_weights', Array, (0, None, (None,), name_type_map['BoneVertDataHalf']), (False, None), (lambda context: context.version >= 335741185, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'skin_transform', name_type_map['NiTransform'], (0, None), (False, None)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 67240192:
			yield 'vertex_weights', Array, (0, None, (instance.num_vertices,), name_type_map['BoneVertData']), (False, None)
		if instance.context.version >= 67240448 and (instance.arg != 0) and (instance.arg != 15):
			yield 'vertex_weights', Array, (0, None, (instance.num_vertices,), name_type_map['BoneVertData']), (False, None)
		if instance.context.version >= 335741185 and instance.arg == 15:
			yield 'vertex_weights', Array, (0, None, (instance.num_vertices,), name_type_map['BoneVertDataHalf']), (False, None)
	def get_transform(self):
		"""Return scale, rotation, and translation into a single 4x4 matrix."""
		return self.skin_transform.get_transform()

	def set_transform(self, mat):
		"""Set rotation, transform, and velocity."""
		self.skin_transform.set_transform(mat)

