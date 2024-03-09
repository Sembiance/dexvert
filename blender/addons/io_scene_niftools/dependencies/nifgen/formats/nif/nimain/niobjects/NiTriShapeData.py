from nifgen.utils.vertex_cache import stripify
from nifgen.utils.tristrip import triangulate
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTriBasedGeomData import NiTriBasedGeomData


class NiTriShapeData(NiTriBasedGeomData):

	"""
	Holds mesh data using a list of singular triangles.
	"""

	__name__ = 'NiTriShapeData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Num Triangles times 3.
		self.num_triangle_points = name_type_map['Uint'](self.context, 0, None)

		# Do we have triangle data?
		self.has_triangles = name_type_map['Bool'](self.context, 0, None)

		# Triangle data.

		# Triangle face data.
		self.triangles = Array(self.context, 0, None, (0,), name_type_map['Triangle'])

		# Number of shared normals groups.
		self.num_match_groups = name_type_map['Ushort'](self.context, 0, None)

		# The shared normals.
		self.match_groups = Array(self.context, 0, None, (0,), name_type_map['MatchGroup'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_triangle_points', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'has_triangles', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'triangles', Array, (0, None, (None,), name_type_map['Triangle']), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'triangles', Array, (0, None, (None,), name_type_map['Triangle']), (False, None), (lambda context: context.version >= 167772419, True)
		yield 'num_match_groups', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 50397184, None)
		yield 'match_groups', Array, (0, None, (None,), name_type_map['MatchGroup']), (False, None), (lambda context: context.version >= 50397184, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_triangle_points', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 167837696:
			yield 'has_triangles', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 167772418:
			yield 'triangles', Array, (0, None, (instance.num_triangles,), name_type_map['Triangle']), (False, None)
		if instance.context.version >= 167772419 and instance.has_triangles:
			yield 'triangles', Array, (0, None, (instance.num_triangles,), name_type_map['Triangle']), (False, None)
		if instance.context.version >= 50397184:
			yield 'num_match_groups', name_type_map['Ushort'], (0, None), (False, None)
			yield 'match_groups', Array, (0, None, (instance.num_match_groups,), name_type_map['MatchGroup']), (False, None)
	"""
	Example usage:

	>>> from pyffi.formats.nif import NifFormat
	>>> block = NifFormat.NiTriShapeData()
	>>> block.set_triangles([(0,1,2),(2,1,3),(2,3,4)])
	>>> block.get_strips()
	[[0, 1, 2, 3, 4]]
	>>> block.get_triangles()
	[(0, 1, 2), (2, 1, 3), (2, 3, 4)]
	>>> block.set_strips([[1,0,1,2,3,4]])
	>>> block.get_strips() # stripifier keeps geometry but nothing else
	[[0, 2, 1, 3], [2, 4, 3]]
	>>> block.get_triangles()
	[(0, 2, 1), (1, 2, 3), (2, 4, 3)]
	"""
	def get_triangles(self):
		return [(t.v_1, t.v_2, t.v_3) for t in self.triangles]

	def set_triangles(self, triangles, stitchstrips = False):
		# note: the stitchstrips argument is ignored - only present to ensure
		# uniform interface between NiTriShapeData and NiTriStripsData

		# initialize triangle array
		n = len(triangles)
		self.num_triangles = n
		self.num_triangle_points = 3*n
		self.has_triangles = (n > 0)
		self.reset_field("triangles")

		# set triangles to triangles array
		for dst_t, src_t in zip(self.triangles, triangles):
			dst_t.v_1, dst_t.v_2, dst_t.v_3 = src_t

	def get_strips(self):
		return stripify(self.get_triangles())

	def set_strips(self, strips):
		self.set_triangles(triangulate(strips))

