from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.matcol.imports import name_type_map


class Layer(BaseStruct):

	__name__ = 'Layer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.info = name_type_map['LayerFrag'](self.context, 0, None)
		self.name = name_type_map['ZString'](self.context, 0, None)
		self.infos = Array(self.context, 0, None, (0,), name_type_map['Info'])
		self.info_names = Array(self.context, 0, None, (0,), name_type_map['ZString'])
		self.attribs = Array(self.context, 0, None, (0,), name_type_map['Attrib'])
		self.attrib_names = Array(self.context, 0, None, (0,), name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'info', name_type_map['LayerFrag'], (0, None), (False, None), (None, None)
		yield 'name', name_type_map['ZString'], (0, None), (False, None), (None, None)
		yield 'infos', Array, (0, None, (None,), name_type_map['Info']), (False, None), (None, None)
		yield 'info_names', Array, (0, None, (None,), name_type_map['ZString']), (False, None), (None, None)
		yield 'attribs', Array, (0, None, (None,), name_type_map['Attrib']), (False, None), (None, None)
		yield 'attrib_names', Array, (0, None, (None,), name_type_map['ZString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'info', name_type_map['LayerFrag'], (0, None), (False, None)
		yield 'name', name_type_map['ZString'], (0, None), (False, None)
		yield 'infos', Array, (0, None, (instance.info.info_count,), name_type_map['Info']), (False, None)
		yield 'info_names', Array, (0, None, (instance.info.info_count,), name_type_map['ZString']), (False, None)
		yield 'attribs', Array, (0, None, (instance.info.attrib_count,), name_type_map['Attrib']), (False, None)
		yield 'attrib_names', Array, (0, None, (instance.info.attrib_count,), name_type_map['ZString']), (False, None)
