from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkWorldObjectCInfo(BaseStruct):

	__name__ = 'bhkWorldObjectCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.broad_phase_type = name_type_map['BroadPhaseType'].BROAD_PHASE_ENTITY
		self.unused_02 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.property = name_type_map['BhkWorldObjCInfoProperty'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)
		yield 'broad_phase_type', name_type_map['BroadPhaseType'], (0, None), (False, name_type_map['BroadPhaseType'].BROAD_PHASE_ENTITY), (None, None)
		yield 'unused_02', Array, (0, None, (3,), name_type_map['Byte']), (False, None), (None, None)
		yield 'property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		yield 'broad_phase_type', name_type_map['BroadPhaseType'], (0, None), (False, name_type_map['BroadPhaseType'].BROAD_PHASE_ENTITY)
		yield 'unused_02', Array, (0, None, (3,), name_type_map['Byte']), (False, None)
		yield 'property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None)
