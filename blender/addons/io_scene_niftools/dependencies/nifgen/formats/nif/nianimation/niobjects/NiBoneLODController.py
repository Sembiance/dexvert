from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiBoneLODController(NiTimeController):

	"""
	DEPRECATED (20.5), Replaced by NiSkinningLODController.
	Level of detail controller for bones.  Priority is arranged from low to high.
	"""

	__name__ = 'NiBoneLODController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.lod = name_type_map['Uint'](self.context, 0, None)

		# Number of LODs.
		self.num_l_o_ds = name_type_map['Uint'](self.context, 0, None)

		# Number of node arrays.
		self.num_node_groups = name_type_map['Uint'](self.context, 0, None)

		# A list of node sets (each set a sequence of bones).
		self.node_groups = Array(self.context, 0, None, (0,), name_type_map['NodeSet'])

		# Number of shape groups.
		self.num_shape_groups = name_type_map['Uint'](self.context, 0, None)

		# List of shape groups.
		self.shape_groups_1 = Array(self.context, 0, None, (0,), name_type_map['SkinInfoSet'])

		# The size of the second list of shape groups.
		self.num_shape_groups_2 = name_type_map['Uint'](self.context, 0, None)

		# Group of NiTriShape indices.
		self.shape_groups_2 = Array(self.context, 0, name_type_map['NiTriBasedGeom'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lod', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_l_o_ds', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_node_groups', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'node_groups', Array, (0, None, (None,), name_type_map['NodeSet']), (False, None), (None, None)
		yield 'num_shape_groups', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 67240448 and context.bs_header.bs_version == 0, None)
		yield 'shape_groups_1', Array, (0, None, (None,), name_type_map['SkinInfoSet']), (False, None), (lambda context: context.version >= 67240448 and context.bs_header.bs_version == 0, None)
		yield 'num_shape_groups_2', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 67240448 and context.bs_header.bs_version == 0, None)
		yield 'shape_groups_2', Array, (0, name_type_map['NiTriBasedGeom'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 67240448 and context.bs_header.bs_version == 0, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lod', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_l_o_ds', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_node_groups', name_type_map['Uint'], (0, None), (False, None)
		yield 'node_groups', Array, (0, None, (instance.num_l_o_ds,), name_type_map['NodeSet']), (False, None)
		if instance.context.version >= 67240448 and instance.context.bs_header.bs_version == 0:
			yield 'num_shape_groups', name_type_map['Uint'], (0, None), (False, None)
			yield 'shape_groups_1', Array, (0, None, (instance.num_shape_groups,), name_type_map['SkinInfoSet']), (False, None)
			yield 'num_shape_groups_2', name_type_map['Uint'], (0, None), (False, None)
			yield 'shape_groups_2', Array, (0, name_type_map['NiTriBasedGeom'], (instance.num_shape_groups_2,), name_type_map['Ref']), (False, None)
