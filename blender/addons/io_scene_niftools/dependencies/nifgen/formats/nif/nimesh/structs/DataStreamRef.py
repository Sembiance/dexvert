from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class DataStreamRef(BaseStruct):

	__name__ = 'DataStreamRef'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Reference to a data stream object which holds the data used by this reference.
		self.stream = name_type_map['Ref'](self.context, 0, name_type_map['NiDataStream'])

		# Sets whether this stream data is per-instance data for use in hardware instancing.
		self.is_per_instance = name_type_map['Bool'].from_value(False)

		# The number of submesh-to-region mappings that this data stream has.
		self.num_submeshes = name_type_map['Ushort'].from_value(1)

		# A lookup table that maps submeshes to regions.
		self.submesh_to_region_map = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.num_components = name_type_map['Uint'].from_value(1)

		# Describes the semantic of each component.
		self.component_semantics = Array(self.context, 0, None, (0,), name_type_map['SemanticData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'stream', name_type_map['Ref'], (0, name_type_map['NiDataStream']), (False, None), (None, None)
		yield 'is_per_instance', name_type_map['Bool'], (0, None), (False, False), (None, None)
		yield 'num_submeshes', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'submesh_to_region_map', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'num_components', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'component_semantics', Array, (0, None, (None,), name_type_map['SemanticData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'stream', name_type_map['Ref'], (0, name_type_map['NiDataStream']), (False, None)
		yield 'is_per_instance', name_type_map['Bool'], (0, None), (False, False)
		yield 'num_submeshes', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'submesh_to_region_map', Array, (0, None, (instance.num_submeshes,), name_type_map['Ushort']), (False, None)
		yield 'num_components', name_type_map['Uint'], (0, None), (False, 1)
		yield 'component_semantics', Array, (0, None, (instance.num_components,), name_type_map['SemanticData']), (False, None)
