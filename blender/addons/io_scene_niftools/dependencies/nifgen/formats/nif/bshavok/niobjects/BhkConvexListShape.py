from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkConvexShapeBase import BhkConvexShapeBase
from nifgen.formats.nif.imports import name_type_map


class BhkConvexListShape(BhkConvexShapeBase):

	"""
	A list of shapes. However,
	- The sub shapes must ALL be convex: Sphere, Capsule, Cylinder, Convex Vertices, Convex Transform
	- The radius of all shapes must be identical
	- The number of sub shapes is restricted to 255
	- The number of vertices of each sub shape is restricted to 255
	
	For this reason you most likely cannot combine Sphere Shapes, Capsule Shapes, and Convex Vertices Shapes,
	as their Radius values differ in function. (Sphere/Capsule radius = physical size, CVS radius = padding/shell)
	
	Shapes collected in a bhkConvexListShape may not have the correct material noise.
	"""

	__name__ = 'bhkConvexListShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_sub_shapes = name_type_map['Uint'].from_value(1)

		# List of shapes. Max of 255.
		self.sub_shapes = Array(self.context, 0, name_type_map['BhkConvexShapeBase'], (0,), name_type_map['Ref'])

		# The material of the shape.
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		self.radius = name_type_map['Float'](self.context, 0, None)
		self.unknown_int_1 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_float_1 = name_type_map['Float'](self.context, 0, None)
		self.child_shape_property = name_type_map['BhkWorldObjCInfoProperty'](self.context, 0, None)

		# If true, an AABB of the children's AABBs is used, which is faster but larger than building an AABB from each child.
		self.use_cached_aabb = name_type_map['Bool'](self.context, 0, None)

		# A distance which is used for getClosestPoint(). If the object being tested is closer, the children are recursed. Otherwise it returns this value.
		self.closest_point_min_distance = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_sub_shapes', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'sub_shapes', Array, (0, name_type_map['BhkConvexShapeBase'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_int_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'child_shape_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None), (None, None)
		yield 'use_cached_aabb', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'closest_point_min_distance', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_sub_shapes', name_type_map['Uint'], (0, None), (False, 1)
		yield 'sub_shapes', Array, (0, name_type_map['BhkConvexShapeBase'], (instance.num_sub_shapes,), name_type_map['Ref']), (False, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown_int_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None)
		yield 'child_shape_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None)
		yield 'use_cached_aabb', name_type_map['Bool'], (0, None), (False, None)
		yield 'closest_point_min_distance', name_type_map['Float'], (0, None), (False, None)
