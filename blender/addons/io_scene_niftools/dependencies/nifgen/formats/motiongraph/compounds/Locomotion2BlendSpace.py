from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Locomotion2BlendSpace(MemStruct):

	"""
	32 bytes
	"""

	__name__ = 'Locomotion2BlendSpace'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.y_axis = name_type_map['BlendSpaceAxis'](self.context, 0, None)
		self.x_axis = name_type_map['BlendSpaceAxis'](self.context, 0, None)
		self.nodes_count = name_type_map['Uint64'](self.context, 0, None)
		self.nodes = name_type_map['ArrayPointer'](self.context, self.nodes_count, name_type_map['Locomotion2BlendSpaceNode'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'y_axis', name_type_map['BlendSpaceAxis'], (0, None), (False, None), (None, None)
		yield 'x_axis', name_type_map['BlendSpaceAxis'], (0, None), (False, None), (None, None)
		yield 'nodes_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'nodes', name_type_map['ArrayPointer'], (None, name_type_map['Locomotion2BlendSpaceNode']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'y_axis', name_type_map['BlendSpaceAxis'], (0, None), (False, None)
		yield 'x_axis', name_type_map['BlendSpaceAxis'], (0, None), (False, None)
		yield 'nodes_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'nodes', name_type_map['ArrayPointer'], (instance.nodes_count, name_type_map['Locomotion2BlendSpaceNode']), (False, None)
