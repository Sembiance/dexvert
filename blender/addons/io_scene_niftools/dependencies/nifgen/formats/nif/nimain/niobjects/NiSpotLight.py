from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiPointLight import NiPointLight


class NiSpotLight(NiPointLight):

	"""
	A spot.
	"""

	__name__ = 'NiSpotLight'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.outer_spot_angle = name_type_map['Float'](self.context, 0, None)
		self.inner_spot_angle = name_type_map['Float'](self.context, 0, None)

		# Describes the distribution of light.
		self.exponent = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'outer_spot_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'inner_spot_angle', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335675397, None)
		yield 'exponent', name_type_map['Float'], (0, None), (False, 1.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'outer_spot_angle', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335675397:
			yield 'inner_spot_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'exponent', name_type_map['Float'], (0, None), (False, 1.0)
