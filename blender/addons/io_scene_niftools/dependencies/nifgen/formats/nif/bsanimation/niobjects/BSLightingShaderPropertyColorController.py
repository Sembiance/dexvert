from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiPoint3InterpController import NiPoint3InterpController


class BSLightingShaderPropertyColorController(NiPoint3InterpController):

	"""
	This controller is used to animate colors in BSLightingShaderProperty.
	"""

	__name__ = 'BSLightingShaderPropertyColorController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Which color in BSLightingShaderProperty to animate.
		self.controlled_color = name_type_map['LightingShaderControlledColor'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'controlled_color', name_type_map['LightingShaderControlledColor'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'controlled_color', name_type_map['LightingShaderControlledColor'], (0, None), (False, None)
