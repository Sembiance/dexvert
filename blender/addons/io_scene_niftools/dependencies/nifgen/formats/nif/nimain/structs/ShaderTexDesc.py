from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class ShaderTexDesc(BaseStruct):

	"""
	NiTexturingProperty::ShaderMap. Shader texture description.
	"""

	__name__ = 'ShaderTexDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.has_map = name_type_map['Bool'](self.context, 0, None)
		self.map = name_type_map['TexDesc'](self.context, 0, None)

		# Unique identifier for the Gamebryo shader system.
		self.map_id = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_map', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'map', name_type_map['TexDesc'], (0, None), (False, None), (None, True)
		yield 'map_id', name_type_map['Uint'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_map', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_map:
			yield 'map', name_type_map['TexDesc'], (0, None), (False, None)
			yield 'map_id', name_type_map['Uint'], (0, None), (False, None)
