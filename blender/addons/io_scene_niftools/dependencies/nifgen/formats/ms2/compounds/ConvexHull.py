from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class ConvexHull(BaseStruct):

	__name__ = 'ConvexHull'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 16 for anubis: 4 hulls * 16 * 12 (size of vert)
		self.vertex_count = name_type_map['Uint'](self.context, 0, None)
		self.rotation = name_type_map['Matrix33'](self.context, 0, None)

		# center of the box
		self.offset = name_type_map['Vector3'](self.context, 0, None)

		# probably padding
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (5,), name_type_map['Uint']), (False, None), (lambda context: context.version == 32, None)
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (lambda context: context.version >= 48, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'vertex_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version == 32:
			yield 'zeros', Array, (0, None, (5,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 48:
			yield 'zeros', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
