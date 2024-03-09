from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiGeometryData import NiGeometryData


class NiLinesData(NiGeometryData):

	"""
	Wireframe geometry data.
	"""

	__name__ = 'NiLinesData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Is vertex connected to other (next?) vertex?
		self.lines = Array(self.context, 0, None, (0,), name_type_map['Bool'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lines', Array, (0, None, (None,), name_type_map['Bool']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lines', Array, (0, None, (instance.num_vertices,), name_type_map['Bool']), (False, None)
