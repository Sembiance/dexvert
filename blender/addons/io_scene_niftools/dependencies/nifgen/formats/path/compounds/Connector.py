from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class Connector(MemStruct):

	__name__ = 'Connector'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.angle_limit = name_type_map['Float'](self.context, 0, None)
		self.direction = name_type_map['Float'](self.context, 0, None)
		self.connector_model = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.joint_model = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'connector_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'joint_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'angle_limit', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'direction', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'connector_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'joint_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'angle_limit', name_type_map['Float'], (0, None), (False, None)
		yield 'direction', name_type_map['Float'], (0, None), (False, None)
