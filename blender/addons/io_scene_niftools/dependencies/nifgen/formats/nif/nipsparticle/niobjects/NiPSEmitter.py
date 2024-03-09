from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSEmitter(NiObject):

	"""
	Abstract base class for all particle emitters.
	"""

	__name__ = 'NiPSEmitter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['NiFixedString'](self.context, 0, None)
		self.speed = name_type_map['Float'](self.context, 0, None)
		self.speed_var = name_type_map['Float'](self.context, 0, None)
		self.speed_flip_ratio = name_type_map['Float'](self.context, 0, None)
		self.declination = name_type_map['Float'](self.context, 0, None)
		self.declination_var = name_type_map['Float'](self.context, 0, None)
		self.planar_angle = name_type_map['Float'](self.context, 0, None)
		self.planar_angle_var = name_type_map['Float'](self.context, 0, None)
		self.color = name_type_map['ByteColor4'](self.context, 0, None)
		self.size = name_type_map['Float'](self.context, 0, None)
		self.size_var = name_type_map['Float'](self.context, 0, None)
		self.lifespan = name_type_map['Float'](self.context, 0, None)
		self.lifespan_var = name_type_map['Float'](self.context, 0, None)
		self.rotation_angle = name_type_map['Float'](self.context, 0, None)
		self.rotation_angle_var = name_type_map['Float'](self.context, 0, None)
		self.rotation_speed = name_type_map['Float'](self.context, 0, None)
		self.rotation_speed_var = name_type_map['Float'](self.context, 0, None)
		self.rotation_axis = name_type_map['Vector3'](self.context, 0, None)
		self.random_rot_speed_sign = name_type_map['Bool'](self.context, 0, None)
		self.random_rot_axis = name_type_map['Bool'](self.context, 0, None)
		self.unknown = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'speed', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'speed_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'speed_flip_ratio', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'declination', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'declination_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'planar_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'planar_angle_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'color', name_type_map['ByteColor4'], (0, None), (False, None), (lambda context: context.version <= 335937536, None)
		yield 'size', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'size_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lifespan', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'lifespan_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'rotation_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'rotation_angle_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'rotation_speed', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'rotation_speed_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'rotation_axis', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'random_rot_speed_sign', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'random_rot_axis', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'unknown', name_type_map['Bool'], (0, None), (False, None), (lambda context: 503316480 <= context.version <= 503316481, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'speed', name_type_map['Float'], (0, None), (False, None)
		yield 'speed_var', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335937792:
			yield 'speed_flip_ratio', name_type_map['Float'], (0, None), (False, None)
		yield 'declination', name_type_map['Float'], (0, None), (False, None)
		yield 'declination_var', name_type_map['Float'], (0, None), (False, None)
		yield 'planar_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'planar_angle_var', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version <= 335937536:
			yield 'color', name_type_map['ByteColor4'], (0, None), (False, None)
		yield 'size', name_type_map['Float'], (0, None), (False, None)
		yield 'size_var', name_type_map['Float'], (0, None), (False, None)
		yield 'lifespan', name_type_map['Float'], (0, None), (False, None)
		yield 'lifespan_var', name_type_map['Float'], (0, None), (False, None)
		yield 'rotation_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'rotation_angle_var', name_type_map['Float'], (0, None), (False, None)
		yield 'rotation_speed', name_type_map['Float'], (0, None), (False, None)
		yield 'rotation_speed_var', name_type_map['Float'], (0, None), (False, None)
		yield 'rotation_axis', name_type_map['Vector3'], (0, None), (False, None)
		yield 'random_rot_speed_sign', name_type_map['Bool'], (0, None), (False, None)
		yield 'random_rot_axis', name_type_map['Bool'], (0, None), (False, None)
		if 503316480 <= instance.context.version <= 503316481:
			yield 'unknown', name_type_map['Bool'], (0, None), (False, None)
