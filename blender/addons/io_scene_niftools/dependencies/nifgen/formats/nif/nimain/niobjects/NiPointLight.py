from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiLight import NiLight


class NiPointLight(NiLight):

	"""
	A point light.
	"""

	__name__ = 'NiPointLight'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.constant_attenuation = name_type_map['Float'](self.context, 0, None)
		self.linear_attenuation = name_type_map['Float'].from_value(1.0)
		self.quadratic_attenuation = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'constant_attenuation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'linear_attenuation', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'quadratic_attenuation', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'constant_attenuation', name_type_map['Float'], (0, None), (False, None)
		yield 'linear_attenuation', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'quadratic_attenuation', name_type_map['Float'], (0, None), (False, None)
