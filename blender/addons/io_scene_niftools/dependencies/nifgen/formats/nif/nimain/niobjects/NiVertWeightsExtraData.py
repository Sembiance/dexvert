from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class NiVertWeightsExtraData(NiExtraData):

	"""
	DEPRECATED (10.x), REMOVED (?)
	Not used in skinning.
	Unsure of use - perhaps for morphing animation or gravity.
	"""

	__name__ = 'NiVertWeightsExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of vertices.
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)

		# The vertex weights.
		self.weight = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'weight', Array, (0, None, (None,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'weight', Array, (0, None, (instance.num_vertices,), name_type_map['Float']), (False, None)
