from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiFloatInterpController import NiFloatInterpController


class BSLightingShaderPropertyFloatController(NiFloatInterpController):

	"""
	This controller is used to animate float variables in BSLightingShaderProperty.
	"""

	__name__ = 'BSLightingShaderPropertyFloatController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Which float variable in BSLightingShaderProperty to animate.
		self.controlled_variable = name_type_map['LightingShaderControlledFloat'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'controlled_variable', name_type_map['LightingShaderControlledFloat'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'controlled_variable', name_type_map['LightingShaderControlledFloat'], (0, None), (False, None)
