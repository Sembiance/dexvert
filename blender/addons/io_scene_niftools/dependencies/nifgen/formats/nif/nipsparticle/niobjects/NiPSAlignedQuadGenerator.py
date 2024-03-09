from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimesh.niobjects.NiMeshModifier import NiMeshModifier


class NiPSAlignedQuadGenerator(NiMeshModifier):

	"""
	A mesh modifier that uses particle system data to generate aligned quads for each particle.
	"""

	__name__ = 'NiPSAlignedQuadGenerator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.scale_amount_u = name_type_map['Float'](self.context, 0, None)
		self.scale_limit_u = name_type_map['Float'].from_value(10000.0)
		self.scale_rest_u = name_type_map['Float'].from_value(1.0)
		self.scale_amount_v = name_type_map['Float'](self.context, 0, None)
		self.scale_limit_v = name_type_map['Float'].from_value(10000.0)
		self.scale_rest_v = name_type_map['Float'].from_value(1.0)
		self.center_u = name_type_map['Float'](self.context, 0, None)
		self.center_v = name_type_map['Float'](self.context, 0, None)
		self.uv_scrolling = name_type_map['Bool'](self.context, 0, None)
		self.num_frames_across = name_type_map['Ushort'].from_value(1)
		self.num_frames_down = name_type_map['Ushort'].from_value(1)
		self.ping_pong = name_type_map['Bool'](self.context, 0, None)
		self.initial_frame = name_type_map['Ushort'](self.context, 0, None)
		self.initial_frame_variation = name_type_map['Float'](self.context, 0, None)
		self.num_frames = name_type_map['Ushort'](self.context, 0, None)
		self.num_frames_variation = name_type_map['Float'](self.context, 0, None)
		self.initial_time = name_type_map['Float'](self.context, 0, None)
		self.final_time = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'scale_amount_u', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'scale_limit_u', name_type_map['Float'], (0, None), (False, 10000.0), (None, None)
		yield 'scale_rest_u', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'scale_amount_v', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'scale_limit_v', name_type_map['Float'], (0, None), (False, 10000.0), (None, None)
		yield 'scale_rest_v', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'center_u', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'center_v', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'uv_scrolling', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'num_frames_across', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'num_frames_down', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'ping_pong', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'initial_frame', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'initial_frame_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'num_frames', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_frames_variation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'initial_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'final_time', name_type_map['Float'], (0, None), (False, 1.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'scale_amount_u', name_type_map['Float'], (0, None), (False, None)
		yield 'scale_limit_u', name_type_map['Float'], (0, None), (False, 10000.0)
		yield 'scale_rest_u', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'scale_amount_v', name_type_map['Float'], (0, None), (False, None)
		yield 'scale_limit_v', name_type_map['Float'], (0, None), (False, 10000.0)
		yield 'scale_rest_v', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'center_u', name_type_map['Float'], (0, None), (False, None)
		yield 'center_v', name_type_map['Float'], (0, None), (False, None)
		yield 'uv_scrolling', name_type_map['Bool'], (0, None), (False, None)
		yield 'num_frames_across', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'num_frames_down', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'ping_pong', name_type_map['Bool'], (0, None), (False, None)
		yield 'initial_frame', name_type_map['Ushort'], (0, None), (False, None)
		yield 'initial_frame_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'num_frames', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_frames_variation', name_type_map['Float'], (0, None), (False, None)
		yield 'initial_time', name_type_map['Float'], (0, None), (False, None)
		yield 'final_time', name_type_map['Float'], (0, None), (False, 1.0)
