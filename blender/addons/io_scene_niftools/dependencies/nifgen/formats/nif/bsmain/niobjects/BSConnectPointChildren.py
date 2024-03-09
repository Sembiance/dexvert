from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BSConnectPointChildren(NiExtraData):

	"""
	Fallout 4 Item Slot Child
	"""

	__name__ = 'BSConnectPoint::Children'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.skinned = name_type_map['Bool'](self.context, 0, None)
		self.num_points = name_type_map['Uint'].from_value(1)
		self.point_name = Array(self.context, 0, None, (0,), name_type_map['SizedString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'skinned', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'num_points', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'point_name', Array, (0, None, (None,), name_type_map['SizedString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'skinned', name_type_map['Bool'], (0, None), (False, None)
		yield 'num_points', name_type_map['Uint'], (0, None), (False, 1)
		yield 'point_name', Array, (0, None, (instance.num_points,), name_type_map['SizedString']), (False, None)
