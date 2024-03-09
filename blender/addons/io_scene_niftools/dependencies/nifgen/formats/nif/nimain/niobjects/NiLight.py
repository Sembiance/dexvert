from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiDynamicEffect import NiDynamicEffect


class NiLight(NiDynamicEffect):

	"""
	Abstract base class that represents light sources in a scene graph.
	For Bethesda Stream 130 (FO4), NiLight now directly inherits from NiAVObject.
	"""

	__name__ = 'NiLight'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Scales the overall brightness of all light components.
		self.dimmer = name_type_map['Float'].from_value(1.0)
		self.ambient_color = name_type_map['Color3'].from_value((0.0, 0.0, 0.0))
		self.diffuse_color = name_type_map['Color3'].from_value((0.0, 0.0, 0.0))
		self.specular_color = name_type_map['Color3'].from_value((0.0, 0.0, 0.0))
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dimmer', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'ambient_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0)), (None, None)
		yield 'diffuse_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0)), (None, None)
		yield 'specular_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0)), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'dimmer', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'ambient_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0))
		yield 'diffuse_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0))
		yield 'specular_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0))
