from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiSkinInstance import NiSkinInstance


class BSDismemberSkinInstance(NiSkinInstance):

	"""
	Bethesda-specific skin instance.
	"""

	__name__ = 'BSDismemberSkinInstance'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_partitions = name_type_map['Uint'].from_value(1)
		self.partitions = Array(self.context, 0, None, (0,), name_type_map['BodyPartList'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_partitions', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'partitions', Array, (0, None, (None,), name_type_map['BodyPartList']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_partitions', name_type_map['Uint'], (0, None), (False, 1)
		yield 'partitions', Array, (0, None, (instance.num_partitions,), name_type_map['BodyPartList']), (False, None)

	def get_dismember_partitions(self):
		"""Return triangles and body part indices."""
		triangles = []
		trianglepartmap = []
		for bodypart, skinpartblock in zip(
			self.partitions, self.skin_partition.partitions):
			if self.skin_partition.vertex_desc:
				# use as proxy for SSE skinpartition, whose triangles don't use the vertex map
				part_triangles = skinpartblock.triangles
			else:
				part_triangles = list(skinpartblock.get_mapped_triangles())
			triangles.extend(part_triangles)
			trianglepartmap += [bodypart.body_part] * len(part_triangles)
		return triangles, trianglepartmap

