from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiVertexColorProperty(NiProperty):

	"""
	Property of vertex colors. This object is referred to by the root object of the NIF file whenever some NiTriShapeData object has vertex colors with non-default settings; if not present, vertex colors have vertex_mode=2 and lighting_mode=1.
	"""

	__name__ = 'NiVertexColorProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['VertexColorFlags'](self.context, 0, None)

		# In Flags from 20.1.0.3 on.
		self.vertex_mode = name_type_map['SourceVertexMode'](self.context, 0, None)

		# In Flags from 20.1.0.3 on.
		self.lighting_mode = name_type_map['LightingMode'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['VertexColorFlags'], (0, None), (False, None), (None, None)
		yield 'vertex_mode', name_type_map['SourceVertexMode'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'lighting_mode', name_type_map['LightingMode'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['VertexColorFlags'], (0, None), (False, None)
		if instance.context.version <= 335544325:
			yield 'vertex_mode', name_type_map['SourceVertexMode'], (0, None), (False, None)
			yield 'lighting_mode', name_type_map['LightingMode'], (0, None), (False, None)
