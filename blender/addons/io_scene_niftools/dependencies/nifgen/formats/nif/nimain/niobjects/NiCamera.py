from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class NiCamera(NiAVObject):

	"""
	Camera object.
	"""

	__name__ = 'NiCamera'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Obsolete flags.
		self.camera_flags = name_type_map['Ushort'](self.context, 0, None)

		# Frustrum left.
		self.frustum_left = name_type_map['Float'].from_value(-0.63707)

		# Frustrum right.
		self.frustum_right = name_type_map['Float'].from_value(0.63707)

		# Frustrum top.
		self.frustum_top = name_type_map['Float'].from_value(0.385714)

		# Frustrum bottom.
		self.frustum_bottom = name_type_map['Float'].from_value(-0.385714)

		# Frustrum near.
		self.frustum_near = name_type_map['Float'].from_value(1.0)

		# Frustrum far.
		self.frustum_far = name_type_map['Float'].from_value(5000.0)

		# Determines whether perspective is used.  Orthographic means no perspective.
		self.use_orthographic_projection = name_type_map['Bool'](self.context, 0, None)

		# Viewport left.
		self.viewport_left = name_type_map['Float'](self.context, 0, None)

		# Viewport right.
		self.viewport_right = name_type_map['Float'].from_value(1.0)

		# Viewport top.
		self.viewport_top = name_type_map['Float'].from_value(1.0)

		# Viewport bottom.
		self.viewport_bottom = name_type_map['Float'](self.context, 0, None)

		# Level of detail adjust.
		self.lod_adjust = name_type_map['Float'].from_value(1.0)
		self.scene = name_type_map['Ref'](self.context, 0, name_type_map['NiAVObject'])

		# Deprecated. Array is always zero length on disk write.
		self.num_screen_polygons = name_type_map['Uint'](self.context, 0, None)

		# Deprecated. Array is always zero length on disk write.
		self.num_screen_textures = name_type_map['Uint'](self.context, 0, None)
		self.unknown_int_3 = name_type_map['Uint'](self.context, 0, None)

		# Always -1?
		self.unknown_q_q_speed_camera_int = name_type_map['Int'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'camera_flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'frustum_left', name_type_map['Float'], (0, None), (False, -0.63707), (None, None)
		yield 'frustum_right', name_type_map['Float'], (0, None), (False, 0.63707), (None, None)
		yield 'frustum_top', name_type_map['Float'], (0, None), (False, 0.385714), (None, None)
		yield 'frustum_bottom', name_type_map['Float'], (0, None), (False, -0.385714), (None, None)
		yield 'frustum_near', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'frustum_far', name_type_map['Float'], (0, None), (False, 5000.0), (None, None)
		yield 'use_orthographic_projection', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'viewport_left', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'viewport_right', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'viewport_top', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'viewport_bottom', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lod_adjust', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'scene', name_type_map['Ref'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'num_screen_polygons', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_screen_textures', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 67240192, None)
		yield 'unknown_int_3', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)
		yield 'unknown_q_q_speed_camera_int', name_type_map['Int'], (0, None), (False, None), (lambda context: 335676695 <= context.version <= 335676695, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837696:
			yield 'camera_flags', name_type_map['Ushort'], (0, None), (False, None)
		yield 'frustum_left', name_type_map['Float'], (0, None), (False, -0.63707)
		yield 'frustum_right', name_type_map['Float'], (0, None), (False, 0.63707)
		yield 'frustum_top', name_type_map['Float'], (0, None), (False, 0.385714)
		yield 'frustum_bottom', name_type_map['Float'], (0, None), (False, -0.385714)
		yield 'frustum_near', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'frustum_far', name_type_map['Float'], (0, None), (False, 5000.0)
		if instance.context.version >= 167837696:
			yield 'use_orthographic_projection', name_type_map['Bool'], (0, None), (False, None)
		yield 'viewport_left', name_type_map['Float'], (0, None), (False, None)
		yield 'viewport_right', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'viewport_top', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'viewport_bottom', name_type_map['Float'], (0, None), (False, None)
		yield 'lod_adjust', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'scene', name_type_map['Ref'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'num_screen_polygons', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 67240192:
			yield 'num_screen_textures', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 50397184:
			yield 'unknown_int_3', name_type_map['Uint'], (0, None), (False, None)
		if 335676695 <= instance.context.version <= 335676695:
			yield 'unknown_q_q_speed_camera_int', name_type_map['Int'], (0, None), (False, None)
