from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.path.imports import name_type_map


class SupportSetRoot(MemStruct):

	__name__ = 'SupportSetRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk_vector_1 = name_type_map['Vector3'](self.context, 0, None)
		self.unk_vector_2 = name_type_map['Vector2'](self.context, 0, None)
		self.unk_vector_3 = name_type_map['Vector3'](self.context, 0, None)
		self.unk_int_1 = name_type_map['Uint'](self.context, 0, None)
		self.num_connector_1 = name_type_map['Uint'](self.context, 0, None)
		self.num_connector_2 = name_type_map['Uint'](self.context, 0, None)
		self.num_pillar = name_type_map['Uint'](self.context, 0, None)
		self.num_footer = name_type_map['Uint'](self.context, 0, None)
		self.num_sub_brace = name_type_map['Uint'](self.context, 0, None)
		self.unk_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.broken_supports = name_type_map['CondPointer'](self.context, 0, name_type_map['BrokeStruct'])
		self.num_data = name_type_map['Uint'](self.context, 0, None)
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.connector_1 = name_type_map['ArrayPointer'](self.context, self.num_connector_1, name_type_map['Connector'])
		self.connector_2 = name_type_map['ArrayPointer'](self.context, self.num_connector_2, name_type_map['ConnectorMultiJoint'])
		self.pillar = name_type_map['ArrayPointer'](self.context, self.num_pillar, name_type_map['Pillar'])
		self.footer = name_type_map['ArrayPointer'](self.context, self.num_footer, name_type_map['Footer'])
		self.sub_braces = name_type_map['ArrayPointer'](self.context, self.num_sub_brace, name_type_map['SubBrace'])
		self.data = name_type_map['ArrayPointer'](self.context, self.num_data, name_type_map['SupportSetData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'connector_1', name_type_map['ArrayPointer'], (None, name_type_map['Connector']), (False, None), (None, None)
		yield 'connector_2', name_type_map['ArrayPointer'], (None, name_type_map['ConnectorMultiJoint']), (False, None), (None, None)
		yield 'pillar', name_type_map['ArrayPointer'], (None, name_type_map['Pillar']), (False, None), (None, None)
		yield 'footer', name_type_map['ArrayPointer'], (None, name_type_map['Footer']), (False, None), (None, None)
		yield 'sub_braces', name_type_map['ArrayPointer'], (None, name_type_map['SubBrace']), (False, None), (None, None)
		yield 'unk_vector_1', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'unk_vector_2', name_type_map['Vector2'], (0, None), (False, None), (None, None)
		yield 'unk_vector_3', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'unk_int_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_connector_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_connector_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_pillar', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_footer', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_sub_brace', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_floats', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, None)
		yield 'broken_supports', name_type_map['CondPointer'], (0, name_type_map['BrokeStruct']), (False, None), (None, None)
		yield 'data', name_type_map['ArrayPointer'], (None, name_type_map['SupportSetData']), (False, None), (None, None)
		yield 'num_data', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, 0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'connector_1', name_type_map['ArrayPointer'], (instance.num_connector_1, name_type_map['Connector']), (False, None)
		yield 'connector_2', name_type_map['ArrayPointer'], (instance.num_connector_2, name_type_map['ConnectorMultiJoint']), (False, None)
		yield 'pillar', name_type_map['ArrayPointer'], (instance.num_pillar, name_type_map['Pillar']), (False, None)
		yield 'footer', name_type_map['ArrayPointer'], (instance.num_footer, name_type_map['Footer']), (False, None)
		yield 'sub_braces', name_type_map['ArrayPointer'], (instance.num_sub_brace, name_type_map['SubBrace']), (False, None)
		yield 'unk_vector_1', name_type_map['Vector3'], (0, None), (False, None)
		yield 'unk_vector_2', name_type_map['Vector2'], (0, None), (False, None)
		yield 'unk_vector_3', name_type_map['Vector3'], (0, None), (False, None)
		yield 'unk_int_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_connector_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_connector_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_pillar', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_footer', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_sub_brace', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_floats', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		yield 'broken_supports', name_type_map['CondPointer'], (0, name_type_map['BrokeStruct']), (False, None)
		yield 'data', name_type_map['ArrayPointer'], (instance.num_data, name_type_map['SupportSetData']), (False, None)
		yield 'num_data', name_type_map['Uint'], (0, None), (False, None)
		yield 'zeros', Array, (0, None, (3,), name_type_map['Uint']), (False, 0)
