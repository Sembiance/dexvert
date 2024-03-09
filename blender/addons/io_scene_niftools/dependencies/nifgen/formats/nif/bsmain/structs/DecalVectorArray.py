from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class DecalVectorArray(BaseStruct):

	"""
	Array of Vectors for Decal placement in BSDecalPlacementVectorExtraData.
	"""

	__name__ = 'DecalVectorArray'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_vectors = name_type_map['Ushort'](self.context, 0, None)

		# Vector XYZ coords
		self.points = Array(self.context, 0, None, (0,), name_type_map['Vector3'])

		# Vector Normals
		self.normals = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_vectors', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'points', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)
		yield 'normals', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_vectors', name_type_map['Ushort'], (0, None), (False, None)
		yield 'points', Array, (0, None, (instance.num_vectors,), name_type_map['Vector3']), (False, None)
		yield 'normals', Array, (0, None, (instance.num_vectors,), name_type_map['Vector3']), (False, None)
