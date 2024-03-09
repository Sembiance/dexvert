import nifgen.formats.nif as NifFormat
from nifgen.utils.inertia import get_mass_center_inertia_polyhedron
from nifgen.utils.mathutils import vecAdd, vecscalarMul, matAdd
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkShapeCollection import BhkShapeCollection
from nifgen.formats.nif.imports import name_type_map


class BhkNiTriStripsShape(BhkShapeCollection):

	"""
	Bethesda custom hkpShapeCollection using NiTriStripsData for geometry storage.
	"""

	__name__ = 'bhkNiTriStripsShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The material of the shape.
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		self.radius = name_type_map['Float'].from_value(0.1)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.grow_by = name_type_map['Uint'].from_value(1)
		self.scale = name_type_map['Vector4'].from_value((1.0, 1.0, 1.0, 0.0))
		self.num_strips_data = name_type_map['Uint'].from_value(1)
		self.strips_data = Array(self.context, 0, name_type_map['NiTriStripsData'], (0,), name_type_map['Ref'])
		self.num_filters = name_type_map['Uint'].from_value(1)
		self.filters = Array(self.context, 0, None, (0,), name_type_map['HavokFilter'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'unused_01', Array, (0, None, (20,), name_type_map['Byte']), (False, None), (None, None)
		yield 'grow_by', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'scale', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0)), (lambda context: context.version >= 167837696, None)
		yield 'num_strips_data', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'strips_data', Array, (0, name_type_map['NiTriStripsData'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_filters', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'filters', Array, (0, None, (None,), name_type_map['HavokFilter']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'unused_01', Array, (0, None, (20,), name_type_map['Byte']), (False, None)
		yield 'grow_by', name_type_map['Uint'], (0, None), (False, 1)
		if instance.context.version >= 167837696:
			yield 'scale', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0))
		yield 'num_strips_data', name_type_map['Uint'], (0, None), (False, 1)
		yield 'strips_data', Array, (0, name_type_map['NiTriStripsData'], (instance.num_strips_data,), name_type_map['Ref']), (False, None)
		yield 'num_filters', name_type_map['Uint'], (0, None), (False, 1)
		yield 'filters', Array, (0, None, (instance.num_filters,), name_type_map['HavokFilter']), (False, None)

	def get_interchangeable_packed_shape(self):
		"""Returns a bhkPackedNiTriStripsShape block that is geometrically
		interchangeable.
		"""
		# get all vertices, triangles, and calculate normals
		vertices = []
		normals = []
		triangles = []
		for strip in self.strips_data:
			triangles.extend(
				(tri1 + len(vertices),
				 tri2 + len(vertices),
				 tri3 + len(vertices))
				for tri1, tri2, tri3 in strip.get_triangles())
			vertices.extend(
				# scaling factor 1/7 applied in add_shape later
				vert.as_tuple() for vert in strip.vertices)
			normals.extend(
				(strip.vertices[tri2] - strip.vertices[tri1]).crossproduct(
					strip.vertices[tri3] - strip.vertices[tri1])
				.normalized(ignore_error=True)
				.as_tuple()
				for tri1, tri2, tri3 in strip.get_triangles())
		# create packed shape and add geometry
		packed = NifFormat.classes.BhkPackedNiTriStripsShape(self.context)
		packed.add_shape(
			triangles=triangles,
			normals=normals,
			vertices=vertices,
			# default layer 1 (static collision)
			layer=self.data_layers[0].layer if self.data_layers else 1,
			material=self.material.material)
		# set scale
		packed.scale_copy.x = 1.0
		packed.scale_copy.y = 1.0
		packed.scale_copy.z = 1.0
		packed.scale.x = 1.0
		packed.scale.y = 1.0
		packed.scale.z = 1.0
		# return result
		return packed

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return mass, center, and inertia tensor."""
		# first find mass, center, and inertia of all shapes
		subshapes_mci = []
		for data in self.strips_data:
			subshapes_mci.append(
				get_mass_center_inertia_polyhedron(
					[ vert.as_tuple() for vert in data.vertices ],
					[ triangle for triangle in data.get_triangles() ],
					density = density, solid = solid))

		# now calculate mass, center, and inertia
		total_mass = 0
		total_center = (0, 0, 0)
		total_inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
		for mass, center, inertia in subshapes_mci:
			total_mass += mass
			total_center = vecAdd(total_center,
								  vecscalarMul(center, mass / total_mass))
			total_inertia = matAdd(total_inertia, inertia)
		return total_mass, total_center, total_inertia

