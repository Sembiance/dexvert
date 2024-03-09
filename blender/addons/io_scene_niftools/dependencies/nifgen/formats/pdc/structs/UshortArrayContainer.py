from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.pdc.imports import name_type_map


class UshortArrayContainer(BaseStruct):

	__name__ = 'UshortArrayContainer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_ushorts = name_type_map['Bigushort'](self.context, 0, None)
		self.ushorts = Array(self.context, 0, None, (0,), name_type_map['Bigushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_ushorts', name_type_map['Bigushort'], (0, None), (False, None), (None, None)
		yield 'ushorts', Array, (0, None, (None,), name_type_map['Bigushort']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_ushorts', name_type_map['Bigushort'], (0, None), (False, None)
		yield 'ushorts', Array, (0, None, (instance.num_ushorts,), name_type_map['Bigushort']), (False, None)
