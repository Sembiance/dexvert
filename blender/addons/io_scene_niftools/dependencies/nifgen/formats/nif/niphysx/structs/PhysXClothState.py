from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class PhysXClothState(BaseStruct):

	__name__ = 'PhysXClothState'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.pose = name_type_map['Matrix34'](self.context, 0, None)
		self.num_vertex_positions = name_type_map['Ushort'](self.context, 0, None)
		self.vertex_positions = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.num_tear_indices = name_type_map['Ushort'](self.context, 0, None)
		self.tear_indices = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.tear_split_planes = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pose', name_type_map['Matrix34'], (0, None), (False, None), (None, None)
		yield 'num_vertex_positions', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'vertex_positions', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)
		yield 'num_tear_indices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'tear_indices', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'tear_split_planes', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pose', name_type_map['Matrix34'], (0, None), (False, None)
		yield 'num_vertex_positions', name_type_map['Ushort'], (0, None), (False, None)
		yield 'vertex_positions', Array, (0, None, (instance.num_vertex_positions,), name_type_map['Vector3']), (False, None)
		yield 'num_tear_indices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'tear_indices', Array, (0, None, (instance.num_tear_indices,), name_type_map['Ushort']), (False, None)
		yield 'tear_split_planes', Array, (0, None, (instance.num_tear_indices,), name_type_map['Vector3']), (False, None)
