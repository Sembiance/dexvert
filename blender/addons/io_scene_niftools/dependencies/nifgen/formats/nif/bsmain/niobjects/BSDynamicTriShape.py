import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.bsmain.niobjects.BSTriShape import BSTriShape
from nifgen.formats.nif.imports import name_type_map


class BSDynamicTriShape(BSTriShape):

	__name__ = 'BSDynamicTriShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dynamic_data_size = name_type_map['Uint'](self.context, 0, None)
		self.vertices = Array(self.context, 0, None, (0,), name_type_map['Vector4'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dynamic_data_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertices', Array, (0, None, (None,), name_type_map['Vector4']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'dynamic_data_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertices', Array, (0, None, (int(instance.dynamic_data_size / 16),), name_type_map['Vector4']), (False, None)

	def apply_scale(self, scale):
		if abs(scale - 1.0) <= NifFormat.EPSILON: return
		super().apply_scale(scale)
		for vertex in self.vertices:
			vertex.x *= scale
			vertex.y *= scale
			vertex.z *= scale

