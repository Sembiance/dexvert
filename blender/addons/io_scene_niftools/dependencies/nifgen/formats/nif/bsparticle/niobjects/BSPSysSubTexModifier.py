from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSPSysSubTexModifier(NiPSysModifier):

	"""
	Similar to a Flip Controller, this handles particle texture animation on a single texture atlas
	"""

	__name__ = 'BSPSysSubTexModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Starting frame/position on atlas
		self.start_frame = name_type_map['Float'](self.context, 0, None)

		# Random chance to start on a different frame?
		self.start_frame_fudge = name_type_map['Float'].from_value(64.0)

		# Ending frame/position on atlas
		self.end_frame = name_type_map['Float'].from_value(63.0)

		# Frame to start looping
		self.loop_start_frame = name_type_map['Float'](self.context, 0, None)
		self.loop_start_frame_fudge = name_type_map['Float'](self.context, 0, None)
		self.frame_count = name_type_map['Float'].from_value(30.0)
		self.frame_count_fudge = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'start_frame', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'start_frame_fudge', name_type_map['Float'], (0, None), (False, 64.0), (None, None)
		yield 'end_frame', name_type_map['Float'], (0, None), (False, 63.0), (None, None)
		yield 'loop_start_frame', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'loop_start_frame_fudge', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'frame_count', name_type_map['Float'], (0, None), (False, 30.0), (None, None)
		yield 'frame_count_fudge', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'start_frame', name_type_map['Float'], (0, None), (False, None)
		yield 'start_frame_fudge', name_type_map['Float'], (0, None), (False, 64.0)
		yield 'end_frame', name_type_map['Float'], (0, None), (False, 63.0)
		yield 'loop_start_frame', name_type_map['Float'], (0, None), (False, None)
		yield 'loop_start_frame_fudge', name_type_map['Float'], (0, None), (False, None)
		yield 'frame_count', name_type_map['Float'], (0, None), (False, 30.0)
		yield 'frame_count_fudge', name_type_map['Float'], (0, None), (False, None)
