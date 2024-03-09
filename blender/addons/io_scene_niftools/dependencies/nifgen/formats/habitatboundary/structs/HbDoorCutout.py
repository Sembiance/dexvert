from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HbDoorCutout(MemStruct):

	"""
	Positions to create door cutout in a wall.
	"""

	__name__ = 'HB_DoorCutout'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Wall cutout height for door.
		self.height = name_type_map['Float'](self.context, 0, None)

		# Wall cutout position for right of door.
		self.right = name_type_map['Float'](self.context, 0, None)

		# Wall cutout position for left of door.
		self.left = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'height', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'right', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'left', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'height', name_type_map['Float'], (0, None), (False, None)
		yield 'right', name_type_map['Float'], (0, None), (False, None)
		yield 'left', name_type_map['Float'], (0, None), (False, None)
