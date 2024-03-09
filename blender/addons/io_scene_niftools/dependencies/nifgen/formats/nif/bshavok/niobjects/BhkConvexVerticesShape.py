import nifgen.formats.nif as NifFormat
from nifgen.utils.inertia import get_mass_center_inertia_polyhedron
from nifgen.utils.quickhull import qhull3d
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkConvexShape import BhkConvexShape
from nifgen.formats.nif.imports import name_type_map


class BhkConvexVerticesShape(BhkConvexShape):

	"""
	A convex shape built from vertices. Note that if the shape is used in
	a non-static object (such as clutter), then they will simply fall
	through ground when they are under a bhkListShape.
	"""

	__name__ = 'bhkConvexVerticesShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.vertices_property = name_type_map['BhkWorldObjCInfoProperty'](self.context, 0, None)
		self.normals_property = name_type_map['BhkWorldObjCInfoProperty'](self.context, 0, None)

		# Number of vertices.
		self.num_vertices = name_type_map['Uint'](self.context, 0, None)

		# Vertices. Fourth component is 0. Lexicographically sorted.
		self.vertices = Array(self.context, 0, None, (0,), name_type_map['Vector4'])

		# The number of half spaces.
		self.num_normals = name_type_map['Uint'](self.context, 0, None)

		# Half spaces as determined by the set of vertices above. First three components define the normal pointing to the exterior, fourth component is the signed distance of the separating plane to the origin: it is minus the dot product of v and n, where v is any vertex on the separating plane, and n is the normal. Lexicographically sorted.
		self.normals = Array(self.context, 0, None, (0,), name_type_map['Vector4'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertices_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None), (None, None)
		yield 'normals_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertices', Array, (0, None, (None,), name_type_map['Vector4']), (False, None), (None, None)
		yield 'num_normals', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'normals', Array, (0, None, (None,), name_type_map['Vector4']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'vertices_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None)
		yield 'normals_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertices', Array, (0, None, (instance.num_vertices,), name_type_map['Vector4']), (False, None)
		yield 'num_normals', name_type_map['Uint'], (0, None), (False, None)
		yield 'normals', Array, (0, None, (instance.num_normals,), name_type_map['Vector4']), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor on data."""
		if abs(scale - 1.0) <= NifFormat.EPSILON: return
		super().apply_scale(scale)
		for v in self.vertices:
			v.x *= scale
			v.y *= scale
			v.z *= scale
		for n in self.normals:
			n.w *= scale

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return mass, center, and inertia tensor."""
		# first find an enumeration of all triangles making up the convex shape
		vertices, triangles = qhull3d(
			[vert.as_tuple() for vert in self.vertices])
		# now calculate mass, center, and inertia
		return get_mass_center_inertia_polyhedron(
			vertices, triangles, density = density, solid = solid)

