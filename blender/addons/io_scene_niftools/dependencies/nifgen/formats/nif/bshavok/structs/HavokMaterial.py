from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HavokMaterial(BaseStruct):

	"""
	Bethesda Havok. Material wrapper for varying material enums by game.
	"""

	__name__ = 'HavokMaterial'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_int = name_type_map['Uint'](self.context, 0, None)

		# The material of the shape.
		self.material = name_type_map['SkyrimHavokMaterial'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_int', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'material', name_type_map['OblivionHavokMaterial'], (0, None), (False, None), (lambda context: context.version <= 335544325 and context.bs_header.bs_version < 16, None)
		yield 'material', name_type_map['Fallout3HavokMaterial'], (0, None), (False, None), (lambda context: (context.version == 335675399) and (context.bs_header.bs_version <= 34), None)
		yield 'material', name_type_map['SkyrimHavokMaterial'], (0, None), (False, None), (lambda context: (context.version == 335675399) and (context.bs_header.bs_version > 34), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167772418:
			yield 'unknown_int', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 335544325 and instance.context.bs_header.bs_version < 16:
			yield 'material', name_type_map['OblivionHavokMaterial'], (0, None), (False, None)
		if (instance.context.version == 335675399) and (instance.context.bs_header.bs_version <= 34):
			yield 'material', name_type_map['Fallout3HavokMaterial'], (0, None), (False, None)
		if (instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 34):
			yield 'material', name_type_map['SkyrimHavokMaterial'], (0, None), (False, None)
