from nifgen.utils.vertex_cache import stripify
from nifgen.utils.tristrip import triangulate
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTriBasedGeomData import NiTriBasedGeomData


class NiTriStripsData(NiTriBasedGeomData):

	"""
	Holds mesh data using strips of triangles.
	"""

	__name__ = 'NiTriStripsData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_strips = name_type_map['Ushort'].from_value(1)

		# The number of points in each triangle strip.
		self.strip_lengths = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# Do we have strip point data?
		self.has_points = name_type_map['Bool'].from_value(True)

		# The points in the Triangle strips.  Size is the sum of all entries in Strip Lengths.

		# The points in the Triangle strips. Size is the sum of all entries in Strip Lengths.
		self.points = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_strips', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'strip_lengths', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'has_points', name_type_map['Bool'], (0, None), (False, True), (lambda context: context.version >= 167772419, None)
		yield 'points', Array, (0, None, (None, None,), name_type_map['Ushort']), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'points', Array, (0, None, (None, None,), name_type_map['Ushort']), (False, None), (lambda context: context.version >= 167772419, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_strips', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'strip_lengths', Array, (0, None, (instance.num_strips,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 167772419:
			yield 'has_points', name_type_map['Bool'], (0, None), (False, True)
		if instance.context.version <= 167772418:
			yield 'points', Array, (0, None, (instance.num_strips, instance.strip_lengths,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 167772419 and instance.has_points:
			yield 'points', Array, (0, None, (instance.num_strips, instance.strip_lengths,), name_type_map['Ushort']), (False, None)
	"""
	Example usage:

	>>> from pyffi.formats.nif import NifFormat
	>>> block = NifFormat.NiTriStripsData()
	>>> block.set_triangles([(0,1,2),(2,1,3),(2,3,4)])
	>>> block.get_strips()
	[[0, 1, 2, 3, 4]]
	>>> block.get_triangles()
	[(0, 1, 2), (1, 3, 2), (2, 3, 4)]
	>>> block.set_strips([[1,0,1,2,3,4]])
	>>> block.get_strips()
	[[1, 0, 1, 2, 3, 4]]
	>>> block.get_triangles()
	[(0, 2, 1), (1, 2, 3), (2, 4, 3)]
	"""
	def get_triangles(self):
		return triangulate(self.points)

	def set_triangles(self, triangles, stitchstrips = False):
		self.set_strips(stripify(
			triangles, stitchstrips=stitchstrips))

	def get_strips(self):
		return [[i for i in strip] for strip in self.points]

	def set_strips(self, strips):
		# initialize strips array
		self.num_strips = len(strips)
		self.reset_field('strip_lengths')
		numtriangles = 0
		for i, strip in enumerate(strips):
			self.strip_lengths[i] = len(strip)
			numtriangles += len(strip) - 2
		self.num_triangles = numtriangles
		self.reset_field('points')
		self.has_points = (len(strips) > 0)

		# copy strips
		for i, strip in enumerate(strips):
			for j, idx in enumerate(strip):
				self.points[i][j] = idx


