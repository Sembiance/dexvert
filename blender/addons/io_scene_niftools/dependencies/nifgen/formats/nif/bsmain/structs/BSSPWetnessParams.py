from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSSPWetnessParams(BaseStruct):

	__name__ = 'BSSPWetnessParams'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.spec_scale = name_type_map['Float'].from_value(-1.0)
		self.spec_power = name_type_map['Float'].from_value(-1.0)
		self.min_var = name_type_map['Float'].from_value(-1.0)
		self.env_map_scale = name_type_map['Float'].from_value(-1.0)
		self.fresnel_power = name_type_map['Float'].from_value(-1.0)
		self.metalness = name_type_map['Float'].from_value(-1.0)
		self.unknown_1 = name_type_map['Float'].from_value(-1.0)
		self.unknown_2 = name_type_map['Float'].from_value(-1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'spec_scale', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'spec_power', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'min_var', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'env_map_scale', name_type_map['Float'], (0, None), (False, -1.0), (lambda context: context.bs_header.bs_version == 130, None)
		yield 'fresnel_power', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'metalness', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'unknown_1', name_type_map['Float'], (0, None), (False, -1.0), (lambda context: context.bs_header.bs_version > 130, None)
		yield 'unknown_2', name_type_map['Float'], (0, None), (False, -1.0), (lambda context: context.bs_header.bs_version == 155, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'spec_scale', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'spec_power', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'min_var', name_type_map['Float'], (0, None), (False, -1.0)
		if instance.context.bs_header.bs_version == 130:
			yield 'env_map_scale', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'fresnel_power', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'metalness', name_type_map['Float'], (0, None), (False, -1.0)
		if instance.context.bs_header.bs_version > 130:
			yield 'unknown_1', name_type_map['Float'], (0, None), (False, -1.0)
		if instance.context.bs_header.bs_version == 155:
			yield 'unknown_2', name_type_map['Float'], (0, None), (False, -1.0)
