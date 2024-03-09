from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackedridecar.imports import name_type_map


class TrackedRideCarRoot(MemStruct):

	"""
	48 bytes
	"""

	__name__ = 'TrackedRideCarRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.sub_count = name_type_map['Uint'](self.context, 0, None)
		self.total_vecs_count = name_type_map['Uint'](self.context, 0, None)
		self.vec = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.zero_0 = name_type_map['Uint'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint64'](self.context, 0, None)
		self.sub = name_type_map['ArrayPointer'](self.context, self.sub_count, name_type_map['TrackedRideCarSub'])
		self.some_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'sub', name_type_map['ArrayPointer'], (None, name_type_map['TrackedRideCarSub']), (False, None), (None, None)
		yield 'sub_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'total_vecs_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vec', Array, (0, None, (3,), name_type_map['Float']), (False, None), (None, None)
		yield 'zero_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'some_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'sub', name_type_map['ArrayPointer'], (instance.sub_count, name_type_map['TrackedRideCarSub']), (False, None)
		yield 'sub_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'total_vecs_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'vec', Array, (0, None, (3,), name_type_map['Float']), (False, None)
		yield 'zero_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'some_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None)
