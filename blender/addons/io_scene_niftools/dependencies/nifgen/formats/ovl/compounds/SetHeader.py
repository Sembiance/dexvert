from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class SetHeader(BaseStruct):

	"""
	defines amount of sets and assets
	"""

	__name__ = 'SetHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.set_count = name_type_map['Uint'](self.context, 0, None)
		self.asset_count = name_type_map['Uint'](self.context, 0, None)

		# must be 1065336831
		self.sig_a = name_type_map['Uint'].from_value(1065336831)

		# must be 16909320
		self.sig_b = name_type_map['Uint'].from_value(16909320)
		self.sets = Array(self.context, 0, None, (0,), name_type_map['SetEntry'])
		self.assets = Array(self.context, 0, None, (0,), name_type_map['AssetEntry'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'set_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'asset_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'sig_a', name_type_map['Uint'], (0, None), (False, 1065336831), (None, None)
		yield 'sig_b', name_type_map['Uint'], (0, None), (False, 16909320), (None, None)
		yield 'sets', Array, (0, None, (None,), name_type_map['SetEntry']), (False, None), (None, None)
		yield 'assets', Array, (0, None, (None,), name_type_map['AssetEntry']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'set_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'asset_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'sig_a', name_type_map['Uint'], (0, None), (False, 1065336831)
		yield 'sig_b', name_type_map['Uint'], (0, None), (False, 16909320)
		yield 'sets', Array, (0, None, (instance.set_count,), name_type_map['SetEntry']), (False, None)
		yield 'assets', Array, (0, None, (instance.asset_count,), name_type_map['AssetEntry']), (False, None)
