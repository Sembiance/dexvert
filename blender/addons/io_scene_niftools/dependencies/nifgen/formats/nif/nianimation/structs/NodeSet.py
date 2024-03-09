from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NodeSet(BaseStruct):

	"""
	A set of NiNode references.
	"""

	__name__ = 'NodeSet'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of node references that follow.
		self.num_nodes = name_type_map['Uint'](self.context, 0, None)

		# The list of NiNode references.
		self.nodes = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_nodes', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'nodes', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ptr']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_nodes', name_type_map['Uint'], (0, None), (False, None)
		yield 'nodes', Array, (0, name_type_map['NiNode'], (instance.num_nodes,), name_type_map['Ptr']), (False, None)
