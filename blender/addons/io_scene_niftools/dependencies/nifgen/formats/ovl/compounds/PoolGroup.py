from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class PoolGroup(BaseStruct):

	"""
	Located at start of deflated archive stream
	"""

	__name__ = 'PoolGroup'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Type of the pools that follow
		self.type = name_type_map['Ushort'](self.context, 0, None)

		# Amount of pools of that type that follow the pool types block
		self.num_pools = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'type', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_pools', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'type', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_pools', name_type_map['Ushort'], (0, None), (False, None)
