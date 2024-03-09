from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiFogProperty(NiProperty):

	"""
	NiFogProperty allows the application to enable, disable and control the appearance of fog.
	"""

	__name__ = 'NiFogProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['FogFlags'](self.context, 0, None)

		# Depth of the fog in normalized units. 1.0 = begins at near plane. 0.5 = begins halfway between the near and far planes.
		self.fog_depth = name_type_map['Float'].from_value(1.0)

		# The color of the fog.
		self.fog_color = name_type_map['Color3'].from_value((0.0, 0.0, 0.0))
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['FogFlags'], (0, None), (False, None), (None, None)
		yield 'fog_depth', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'fog_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0)), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['FogFlags'], (0, None), (False, None)
		yield 'fog_depth', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'fog_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0))
