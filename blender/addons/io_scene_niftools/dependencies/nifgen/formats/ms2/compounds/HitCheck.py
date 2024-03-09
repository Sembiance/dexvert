from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class HitCheck(BaseStruct):

	"""
	JWE2: 20 bytes excluding collider
	"""

	__name__ = 'HitCheck'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dtype = name_type_map['CollisionType'](self.context, 0, None)

		# PZ, JWE2 always 0
		self.flag_0 = name_type_map['Ushort'].from_value(0)

		# JWE: 16; PZ, JWE2 always 0
		self.flag_1 = name_type_map['Ushort'].from_value(0)

		# probably a bitfield, not sure though, might be a list of ubytes too
		self.collision_layers = name_type_map['Uint64'](self.context, 0, None)
		self.collision_ignore = name_type_map['OffsetString'](self.context, self.arg, None)
		self.collision_use = name_type_map['OffsetString'](self.context, self.arg, None)

		# ?
		self.zero_extra_pc = name_type_map['Uint'](self.context, 0, None)
		self.name = name_type_map['OffsetString'](self.context, self.arg, None)
		self.collider = name_type_map['MeshCollision'](self.context, 0, None)

		# ?
		self.zero_extra_zt = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dtype', name_type_map['CollisionType'], (0, None), (False, None), (None, None)
		yield 'flag_0', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'flag_1', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'collision_layers', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version <= 47, None)
		yield 'collision_ignore', name_type_map['OffsetString'], (None, None), (False, None), (lambda context: context.version >= 48, None)
		yield 'collision_use', name_type_map['OffsetString'], (None, None), (False, None), (lambda context: context.version >= 48, None)
		yield 'zero_extra_pc', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'name', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'collider', name_type_map['Sphere'], (0, None), (False, None), (None, True)
		yield 'collider', name_type_map['BoundingBox'], (0, None), (False, None), (None, True)
		yield 'collider', name_type_map['Capsule'], (0, None), (False, None), (None, True)
		yield 'collider', name_type_map['Cylinder'], (0, None), (False, None), (None, True)
		yield 'collider', name_type_map['ConvexHull'], (0, None), (False, None), (None, True)
		yield 'collider', name_type_map['ConvexHull'], (0, None), (False, None), (None, True)
		yield 'collider', name_type_map['MeshCollision'], (0, None), (False, None), (None, True)
		yield 'zero_extra_zt', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version == 13, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'dtype', name_type_map['CollisionType'], (0, None), (False, None)
		yield 'flag_0', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'flag_1', name_type_map['Ushort'], (0, None), (False, 0)
		if instance.context.version <= 47:
			yield 'collision_layers', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version >= 48:
			yield 'collision_ignore', name_type_map['OffsetString'], (instance.arg, None), (False, None)
			yield 'collision_use', name_type_map['OffsetString'], (instance.arg, None), (False, None)
		if instance.context.version <= 32:
			yield 'zero_extra_pc', name_type_map['Uint'], (0, None), (False, None)
		yield 'name', name_type_map['OffsetString'], (instance.arg, None), (False, None)
		if instance.dtype == 0:
			yield 'collider', name_type_map['Sphere'], (0, None), (False, None)
		if instance.dtype == 1:
			yield 'collider', name_type_map['BoundingBox'], (0, None), (False, None)
		if instance.dtype == 2:
			yield 'collider', name_type_map['Capsule'], (0, None), (False, None)
		if instance.dtype == 3:
			yield 'collider', name_type_map['Cylinder'], (0, None), (False, None)
		if instance.dtype == 7:
			yield 'collider', name_type_map['ConvexHull'], (0, None), (False, None)
		if instance.dtype == 8:
			yield 'collider', name_type_map['ConvexHull'], (0, None), (False, None)
		if instance.dtype == 10:
			yield 'collider', name_type_map['MeshCollision'], (0, None), (False, None)
		if instance.context.version == 13:
			yield 'zero_extra_zt', name_type_map['Uint'], (0, None), (False, None)
