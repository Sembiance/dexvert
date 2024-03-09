from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSConnectPoint(BaseStruct):

	__name__ = 'BSConnectPoint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.parent = name_type_map['SizedString'].from_value('WorkshopConnectPoints')
		self.name = name_type_map['SizedString'](self.context, 0, None)
		self.rotation = name_type_map['Quaternion'](self.context, 0, None)
		self.translation = name_type_map['Vector3'](self.context, 0, None)
		self.scale = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'parent', name_type_map['SizedString'], (0, None), (False, 'WorkshopConnectPoints'), (None, None)
		yield 'name', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['Quaternion'], (0, None), (False, None), (None, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'parent', name_type_map['SizedString'], (0, None), (False, 'WorkshopConnectPoints')
		yield 'name', name_type_map['SizedString'], (0, None), (False, None)
		yield 'rotation', name_type_map['Quaternion'], (0, None), (False, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0)
