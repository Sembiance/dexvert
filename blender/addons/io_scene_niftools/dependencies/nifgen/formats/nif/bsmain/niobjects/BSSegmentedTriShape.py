from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTriShape import NiTriShape


class BSSegmentedTriShape(NiTriShape):

	"""
	Bethesda-specific AV object.
	"""

	__name__ = 'BSSegmentedTriShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of segments in the square grid
		self.num_segments = name_type_map['Uint'].from_value(16)

		# Configuration of each segment
		self.segment = Array(self.context, 0, None, (0,), name_type_map['BSGeometrySegmentData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_segments', name_type_map['Uint'], (0, None), (False, 16), (None, None)
		yield 'segment', Array, (0, None, (None,), name_type_map['BSGeometrySegmentData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_segments', name_type_map['Uint'], (0, None), (False, 16)
		yield 'segment', Array, (0, None, (instance.num_segments,), name_type_map['BSGeometrySegmentData']), (False, None)
