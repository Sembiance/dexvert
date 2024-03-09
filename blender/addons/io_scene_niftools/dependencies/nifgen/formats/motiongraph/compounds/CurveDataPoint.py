from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class CurveDataPoint(MemStruct):

	"""
	12 bytes
	"""

	__name__ = 'CurveDataPoint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.x = name_type_map['Float'](self.context, 0, None)
		self.y = name_type_map['Short'](self.context, 0, None)
		self.sub_curve_type = name_type_map['SubCurveType'](self.context, 0, None)
		self.subsequent_curve_param = name_type_map['Short'](self.context, 0, None)
		self.subsequent_curve_param_b = name_type_map['Short'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'x', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'sub_curve_type', name_type_map['SubCurveType'], (0, None), (False, None), (None, None)
		yield 'subsequent_curve_param', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'subsequent_curve_param_b', name_type_map['Short'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'x', name_type_map['Float'], (0, None), (False, None)
		yield 'y', name_type_map['Short'], (0, None), (False, None)
		yield 'sub_curve_type', name_type_map['SubCurveType'], (0, None), (False, None)
		yield 'subsequent_curve_param', name_type_map['Short'], (0, None), (False, None)
		yield 'subsequent_curve_param_b', name_type_map['Short'], (0, None), (False, None)
