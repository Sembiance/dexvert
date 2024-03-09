import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class BSTriShape(NiAVObject):

	"""
	Fallout 4 Tri Shape
	"""

	__name__ = 'BSTriShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)
		self.bound_min_max = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.skin = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])
		self.shader_property = name_type_map['Ref'](self.context, 0, name_type_map['BSShaderProperty'])
		self.alpha_property = name_type_map['Ref'](self.context, 0, name_type_map['NiAlphaProperty'])
		self.vertex_desc = name_type_map['BSVertexDesc'](self.context, 0, None)
		self.num_triangles = name_type_map['Ushort'](self.context, 0, None)
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)
		self.data_size = name_type_map['Uint'](self.context, 0, None)
		self.vertex_data = Array(self.context, self.vertex_desc >> 44, None, (0,), name_type_map['BSVertexDataSSE'])
		self.triangles = Array(self.context, 0, None, (0,), name_type_map['Triangle'])
		self.particle_data_size = name_type_map['Uint'](self.context, 0, None)
		self.particle_vertices = Array(self.context, 0, None, (0,), name_type_map['HalfVector3'])
		self.particle_normals = Array(self.context, 0, None, (0,), name_type_map['HalfVector3'])
		self.particle_triangles = Array(self.context, 0, None, (0,), name_type_map['Triangle'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, None)
		yield 'bound_min_max', Array, (0, None, (6,), name_type_map['Float']), (False, None), (lambda context: context.bs_header.bs_version == 155, None)
		yield 'skin', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (None, None)
		yield 'shader_property', name_type_map['Ref'], (0, name_type_map['BSShaderProperty']), (False, None), (None, None)
		yield 'alpha_property', name_type_map['Ref'], (0, name_type_map['NiAlphaProperty']), (False, None), (None, None)
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None), (None, None)
		yield 'num_triangles', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'data_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertex_data', Array, (None, None, (None,), name_type_map['BSVertexData']), (False, None), (lambda context: context.bs_header.bs_version >= 130, True)
		yield 'vertex_data', Array, (None, None, (None,), name_type_map['BSVertexDataSSE']), (False, None), (lambda context: context.bs_header.bs_version == 100, True)
		yield 'triangles', Array, (0, None, (None,), name_type_map['Triangle']), (False, None), (None, True)
		yield 'particle_data_size', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 100, None)
		yield 'particle_vertices', Array, (0, None, (None,), name_type_map['HalfVector3']), (False, None), (lambda context: context.bs_header.bs_version == 100, True)
		yield 'particle_normals', Array, (0, None, (None,), name_type_map['HalfVector3']), (False, None), (lambda context: context.bs_header.bs_version == 100, True)
		yield 'particle_triangles', Array, (0, None, (None,), name_type_map['Triangle']), (False, None), (lambda context: context.bs_header.bs_version == 100, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 155:
			yield 'bound_min_max', Array, (0, None, (6,), name_type_map['Float']), (False, None)
		yield 'skin', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
		yield 'shader_property', name_type_map['Ref'], (0, name_type_map['BSShaderProperty']), (False, None)
		yield 'alpha_property', name_type_map['Ref'], (0, name_type_map['NiAlphaProperty']), (False, None)
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 130:
			yield 'num_triangles', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.bs_header.bs_version < 130:
			yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'data_size', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 130 and instance.data_size > 0:
			yield 'vertex_data', Array, (instance.vertex_desc >> 44, None, (instance.num_vertices,), name_type_map['BSVertexData']), (False, None)
		if instance.context.bs_header.bs_version == 100 and instance.data_size > 0:
			yield 'vertex_data', Array, (instance.vertex_desc >> 44, None, (instance.num_vertices,), name_type_map['BSVertexDataSSE']), (False, None)
		if instance.data_size > 0:
			yield 'triangles', Array, (0, None, (instance.num_triangles,), name_type_map['Triangle']), (False, None)
		if instance.context.bs_header.bs_version == 100:
			yield 'particle_data_size', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 100 and instance.particle_data_size > 0:
			yield 'particle_vertices', Array, (0, None, (instance.num_vertices,), name_type_map['HalfVector3']), (False, None)
			yield 'particle_normals', Array, (0, None, (instance.num_vertices,), name_type_map['HalfVector3']), (False, None)
			yield 'particle_triangles', Array, (0, None, (instance.num_triangles,), name_type_map['Triangle']), (False, None)

	def update_center_radius(self):
		"""Recalculate center and radius of the data."""
		# in case there are no vertices, set center and radius to zero
		if len(self.vertex_data) == 0:
			self.bounding_sphere.center.x = 0.0
			self.bounding_sphere.center.y = 0.0
			self.bounding_sphere.center.z = 0.0
			self.bounding_sphere.radius = 0.0
			return

		vertices = [data.vertex for data in self.vertex_data]
		# find extreme values in x, y, and z direction
		lowx = min([v.x for v in vertices])
		lowy = min([v.y for v in vertices])
		lowz = min([v.z for v in vertices])
		highx = max([v.x for v in vertices])
		highy = max([v.y for v in vertices])
		highz = max([v.z for v in vertices])

		# center is in the center of the bounding box
		cx = (lowx + highx) * 0.5
		cy = (lowy + highy) * 0.5
		cz = (lowz + highz) * 0.5
		self.bounding_sphere.center.x = cx
		self.bounding_sphere.center.y = cy
		self.bounding_sphere.center.z = cz

		# radius is the largest distance from the center
		r2 = 0.0
		for v in vertices:
			dx = cx - v.x
			dy = cy - v.y
			dz = cz - v.z
			r2 = max(r2, dx*dx+dy*dy+dz*dz)
		self.bounding_sphere.radius = r2 ** 0.5

	def apply_scale(self, scale):
		if abs(scale - 1.0) <= NifFormat.EPSILON: return
		super().apply_scale(scale)
		self.bounding_sphere.apply_scale(scale)
		for v_data in self.vertex_data:
			v = v_data.vertex
			v.x *= scale
			v.y *= scale
			v.z *= scale

	def get_triangles(self):
		"""Return triangles"""
		if self.vertex_desc.vertex_attributes.skinned:
			# triangles are found in the partition
			triangles = []
			if self.skin:
				for partition in self.skin.skin_partition.partitions:
                    # there is a vertex map, but it doesn't seem to be used
					if partition.has_faces:
						triangles.extend(partition.triangles)
			return triangles
		else:
			return self.triangles

	def get_vertex_data(self):
		vertex_data = self.vertex_data
		if self.vertex_desc.vertex_attributes.skinned:
			if self.skin:
				if self.skin.skin_partition:
					vertex_data = self.skin.skin_partition.vertex_data
		return vertex_data

	def is_skin(self):
		"""Returns True if geometry is skinned."""
		return self.skin != None

	@property
	def skin_instance(self):
		return self.skin

	@skin_instance.setter
	def skin_instance(self, value):
		self.skin = value

