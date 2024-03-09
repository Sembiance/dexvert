from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HbPhysicsOffsets(MemStruct):

	"""
	Physics values for barriers.
	"""

	__name__ = 'HB_PhysicsOffsets'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Wall thickness. Affects navcut, selection, and climb nav width. Must be under a certain value or it crashes.
		self.thickness = name_type_map['Float'](self.context, 0, None)
		self.post_size = name_type_map['HbPostSize'](self.context, 0, None)

		# Wall size above wall_height. Affects navcut, selection, and climb nav height.
		self.wall_pad_top = name_type_map['Float'](self.context, 0, None)

		# Distance between post center and start of wall. Larger values create a visual and nav gap between the post and wall segment.
		self.wall_post_gap = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'thickness', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'post_size', name_type_map['HbPostSize'], (0, None), (False, None), (None, None)
		yield 'wall_pad_top', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'wall_post_gap', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'thickness', name_type_map['Float'], (0, None), (False, None)
		yield 'post_size', name_type_map['HbPostSize'], (0, None), (False, None)
		yield 'wall_pad_top', name_type_map['Float'], (0, None), (False, None)
		yield 'wall_post_gap', name_type_map['Float'], (0, None), (False, None)
