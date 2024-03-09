from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HavokFilter(BaseStruct):

	"""
	Bethesda Havok. Collision filter info representing Layer, Flags, Part Number, and Group all combined into one uint.
	"""

	__name__ = 'HavokFilter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The layer the collision belongs to.
		self.layer = name_type_map['SkyrimLayer'].SKYL_STATIC
		self.flags = name_type_map['CollisionFilterFlags'].from_value(0)
		self.group = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'layer', name_type_map['OblivionLayer'], (0, None), (False, name_type_map['OblivionLayer'].OL_STATIC), (lambda context: context.version <= 335544325 and context.bs_header.bs_version < 16, None)
		yield 'layer', name_type_map['Fallout3Layer'], (0, None), (False, name_type_map['Fallout3Layer'].FOL_STATIC), (lambda context: (context.version == 335675399) and (context.bs_header.bs_version <= 34), None)
		yield 'layer', name_type_map['SkyrimLayer'], (0, None), (False, name_type_map['SkyrimLayer'].SKYL_STATIC), (lambda context: (context.version == 335675399) and (context.bs_header.bs_version > 34), None)
		yield 'flags', name_type_map['CollisionFilterFlags'], (0, None), (False, 0), (None, None)
		yield 'group', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 335544325 and instance.context.bs_header.bs_version < 16:
			yield 'layer', name_type_map['OblivionLayer'], (0, None), (False, name_type_map['OblivionLayer'].OL_STATIC)
		if (instance.context.version == 335675399) and (instance.context.bs_header.bs_version <= 34):
			yield 'layer', name_type_map['Fallout3Layer'], (0, None), (False, name_type_map['Fallout3Layer'].FOL_STATIC)
		if (instance.context.version == 335675399) and (instance.context.bs_header.bs_version > 34):
			yield 'layer', name_type_map['SkyrimLayer'], (0, None), (False, name_type_map['SkyrimLayer'].SKYL_STATIC)
		yield 'flags', name_type_map['CollisionFilterFlags'], (0, None), (False, 0)
		yield 'group', name_type_map['Ushort'], (0, None), (False, None)
