from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiFloatExtraData import NiFloatExtraData


class BSDecalPlacementVectorExtraData(NiFloatExtraData):

	"""
	Bethesda-specific extra data. Lists locations and normals on a mesh that are appropriate for decal placement.
	"""

	__name__ = 'BSDecalPlacementVectorExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_vector_blocks = name_type_map['Ushort'](self.context, 0, None)
		self.vector_blocks = Array(self.context, 0, None, (0,), name_type_map['DecalVectorArray'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_vector_blocks', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'vector_blocks', Array, (0, None, (None,), name_type_map['DecalVectorArray']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_vector_blocks', name_type_map['Ushort'], (0, None), (False, None)
		yield 'vector_blocks', Array, (0, None, (instance.num_vector_blocks,), name_type_map['DecalVectorArray']), (False, None)
