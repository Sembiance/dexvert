from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class ConnectorMultiJoint(MemStruct):

	__name__ = 'ConnectorMultiJoint'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.padding = name_type_map['Uint64'].from_value(0)
		self.num_joints = name_type_map['Uint'](self.context, 0, None)
		self.unk_float_1 = name_type_map['Float'](self.context, 0, None)
		self.unk_float_2 = name_type_map['Float'](self.context, 0, None)
		self.unk_int_1 = name_type_map['Uint'](self.context, 0, None)
		self.connector_model = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.joints = name_type_map['ArrayPointer'](self.context, self.num_joints, name_type_map['Joint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'connector_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'padding', name_type_map['Uint64'], (0, None), (False, 0), (None, None)
		yield 'joints', name_type_map['ArrayPointer'], (None, name_type_map['Joint']), (False, None), (None, None)
		yield 'num_joints', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_float_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_float_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_int_1', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'connector_model', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'padding', name_type_map['Uint64'], (0, None), (False, 0)
		yield 'joints', name_type_map['ArrayPointer'], (instance.num_joints, name_type_map['Joint']), (False, None)
		yield 'num_joints', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_float_1', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_float_2', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_int_1', name_type_map['Uint'], (0, None), (False, None)
