from nifgen.formats.bani.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class BaniRoot(MemStruct):

	"""
	24 bytes This varies per bani animation file and describes the bani's frames and duration
	"""

	__name__ = 'BaniRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The frame in the banis where this bani starts reading
		self.read_start_frame = name_type_map['Uint'](self.context, 0, None)

		# Number of frames in this bani file
		self.num_frames = name_type_map['Uint'](self.context, 0, None)

		# length of the animation, can easily get keyframe spacing now
		self.animation_length = name_type_map['Float'](self.context, 0, None)

		# if 1381323599 then looped
		self.loop_flag = name_type_map['Uint'](self.context, 0, None)

		# points to the banis file used
		self.banis = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'banis', name_type_map['Pointer'], (0, None), (False, None), (None, None)
		yield 'read_start_frame', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_frames', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'animation_length', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'loop_flag', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'banis', name_type_map['Pointer'], (0, None), (False, None)
		yield 'read_start_frame', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_frames', name_type_map['Uint'], (0, None), (False, None)
		yield 'animation_length', name_type_map['Float'], (0, None), (False, None)
		yield 'loop_flag', name_type_map['Uint'], (0, None), (False, None)
