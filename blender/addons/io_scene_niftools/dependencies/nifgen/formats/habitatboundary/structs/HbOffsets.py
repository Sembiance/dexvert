from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HbOffsets(MemStruct):

	__name__ = 'HB_Offsets'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.physics = name_type_map['HbPhysicsOffsets'](self.context, 0, None)

		# Vertical offset of visible post above wall. Post height = wall_height + post_height_offset.
		self.post_height_offset = name_type_map['Float'](self.context, 0, None)

		# The starting height of the barrier wall.
		self.wall_height = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'physics', name_type_map['HbPhysicsOffsets'], (0, None), (False, None), (None, None)
		yield 'post_height_offset', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'wall_height', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'physics', name_type_map['HbPhysicsOffsets'], (0, None), (False, None)
		yield 'post_height_offset', name_type_map['Float'], (0, None), (False, None)
		yield 'wall_height', name_type_map['Float'], (0, None), (False, None)
