from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class OldSkinData(BaseStruct):

	"""
	Used to store skin weights in NiTriShapeSkinController.
	"""

	__name__ = 'OldSkinData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The amount that this bone affects the vertex.
		self.vertex_weight = name_type_map['Float'](self.context, 0, None)

		# The index of the vertex that this weight applies to.
		self.vertex_index = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_vector = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertex_weight', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'vertex_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_vector', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'vertex_weight', name_type_map['Float'], (0, None), (False, None)
		yield 'vertex_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_vector', name_type_map['Vector3'], (0, None), (False, None)
