from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BSConnectPointParents(NiExtraData):

	"""
	Fallout 4 Item Slot Parent
	"""

	__name__ = 'BSConnectPoint::Parents'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_connect_points = name_type_map['Uint'].from_value(1)
		self.connect_points = Array(self.context, 0, None, (0,), name_type_map['BSConnectPoint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_connect_points', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'connect_points', Array, (0, None, (None,), name_type_map['BSConnectPoint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_connect_points', name_type_map['Uint'], (0, None), (False, 1)
		yield 'connect_points', Array, (0, None, (instance.num_connect_points,), name_type_map['BSConnectPoint']), (False, None)
