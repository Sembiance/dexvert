from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackedridecar.imports import name_type_map


class TrackedRideCarSub(MemStruct):

	"""
	32 bytes
	"""

	__name__ = 'TrackedRideCarSub'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.float = name_type_map['Float'](self.context, 0, None)
		self.u_0 = name_type_map['Uint'](self.context, 0, None)
		self.vecs_count = name_type_map['Uint64'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint64'](self.context, 0, None)
		self.vectors = name_type_map['ArrayPointer'](self.context, self.vecs_count, name_type_map['Vector3'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'float', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vectors', name_type_map['ArrayPointer'], (None, name_type_map['Vector3']), (False, None), (None, None)
		yield 'vecs_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'float', name_type_map['Float'], (0, None), (False, None)
		yield 'u_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'vectors', name_type_map['ArrayPointer'], (instance.vecs_count, name_type_map['Vector3']), (False, None)
		yield 'vecs_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero_1', name_type_map['Uint64'], (0, None), (False, None)
