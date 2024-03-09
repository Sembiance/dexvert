from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class CurveData(MemStruct):

	"""
	16 bytes
	"""

	__name__ = 'CurveData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.points = name_type_map['Pointer'](self.context, self.count, name_type_map['CurveDataPoints'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'points', name_type_map['Pointer'], (None, name_type_map['CurveDataPoints']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'points', name_type_map['Pointer'], (instance.count, name_type_map['CurveDataPoints']), (False, None)
