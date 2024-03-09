from nifgen.array import Array
from nifgen.formats.nif.bsmain.niobjects.BSMultiBoundNode import BSMultiBoundNode
from nifgen.formats.nif.imports import name_type_map


class BSDistantObjectInstancedNode(BSMultiBoundNode):

	__name__ = 'BSDistantObjectInstancedNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_instances = name_type_map['Uint'](self.context, 0, None)
		self.instances = Array(self.context, 0, None, (0,), name_type_map['BSDistantObjectInstance'])
		self.texture_arrays = Array(self.context, 0, None, (0,), name_type_map['BSShaderTextureArray'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_instances', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'instances', Array, (0, None, (None,), name_type_map['BSDistantObjectInstance']), (False, None), (None, None)
		yield 'texture_arrays', Array, (0, None, (3,), name_type_map['BSShaderTextureArray']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_instances', name_type_map['Uint'], (0, None), (False, None)
		yield 'instances', Array, (0, None, (instance.num_instances,), name_type_map['BSDistantObjectInstance']), (False, None)
		yield 'texture_arrays', Array, (0, None, (3,), name_type_map['BSShaderTextureArray']), (False, None)
