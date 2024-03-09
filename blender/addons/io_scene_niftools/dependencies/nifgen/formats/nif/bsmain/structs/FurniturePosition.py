from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class FurniturePosition(BaseStruct):

	"""
	Bethesda Animation. Describes a furniture position?
	"""

	__name__ = 'FurniturePosition'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Offset of furniture marker.
		self.offset = name_type_map['Vector3'](self.context, 0, None)

		# Furniture marker orientation.
		self.orientation = name_type_map['Ushort'](self.context, 0, None)

		# Refers to a furnituremarkerxx.nif file. Always seems to be the same as Position Ref 2.
		self.position_ref_1 = name_type_map['Byte'](self.context, 0, None)

		# Refers to a furnituremarkerxx.nif file. Always seems to be the same as Position Ref 1.
		self.position_ref_2 = name_type_map['Byte'](self.context, 0, None)

		# Rotation around z-axis in radians.
		self.heading = name_type_map['Float'](self.context, 0, None)
		self.animation_type = name_type_map['AnimationType'](self.context, 0, None)
		self.entry_properties = name_type_map['FurnitureEntryPoints'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'orientation', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'position_ref_1', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'position_ref_2', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'heading', name_type_map['Float'], (0, None), (False, None), (lambda context: context.bs_header.bs_version > 34, None)
		yield 'animation_type', name_type_map['AnimationType'], (0, None), (False, None), (lambda context: context.bs_header.bs_version > 34, None)
		yield 'entry_properties', name_type_map['FurnitureEntryPoints'], (0, None), (False, None), (lambda context: context.bs_header.bs_version > 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.bs_header.bs_version <= 34:
			yield 'orientation', name_type_map['Ushort'], (0, None), (False, None)
			yield 'position_ref_1', name_type_map['Byte'], (0, None), (False, None)
			yield 'position_ref_2', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.bs_header.bs_version > 34:
			yield 'heading', name_type_map['Float'], (0, None), (False, None)
			yield 'animation_type', name_type_map['AnimationType'], (0, None), (False, None)
			yield 'entry_properties', name_type_map['FurnitureEntryPoints'], (0, None), (False, None)
