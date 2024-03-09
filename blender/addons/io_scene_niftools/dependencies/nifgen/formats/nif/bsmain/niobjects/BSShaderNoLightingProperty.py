from nifgen.formats.nif.bsmain.niobjects.BSShaderLightingProperty import BSShaderLightingProperty
from nifgen.formats.nif.imports import name_type_map


class BSShaderNoLightingProperty(BSShaderLightingProperty):

	"""
	Bethesda-specific property.
	"""

	__name__ = 'BSShaderNoLightingProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The texture glow map.
		self.file_name = name_type_map['SizedString'](self.context, 0, None)

		# At this cosine of angle falloff will be equal to Falloff Start Opacity
		self.falloff_start_angle = name_type_map['Float'].from_value(1.0)

		# At this cosine of angle falloff will be equal to Falloff Stop Opacity
		self.falloff_stop_angle = name_type_map['Float'].from_value(0.0)

		# Alpha falloff multiplier at start angle
		self.falloff_start_opacity = name_type_map['Float'].from_value(1.0)

		# Alpha falloff multiplier at end angle
		self.falloff_stop_opacity = name_type_map['Float'].from_value(0.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_name', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'falloff_start_angle', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version > 26, None)
		yield 'falloff_stop_angle', name_type_map['Float'], (0, None), (False, 0.0), (lambda context: context.bs_header.bs_version > 26, None)
		yield 'falloff_start_opacity', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version > 26, None)
		yield 'falloff_stop_opacity', name_type_map['Float'], (0, None), (False, 0.0), (lambda context: context.bs_header.bs_version > 26, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_name', name_type_map['SizedString'], (0, None), (False, None)
		if instance.context.bs_header.bs_version > 26:
			yield 'falloff_start_angle', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'falloff_stop_angle', name_type_map['Float'], (0, None), (False, 0.0)
			yield 'falloff_start_opacity', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'falloff_stop_opacity', name_type_map['Float'], (0, None), (False, 0.0)
