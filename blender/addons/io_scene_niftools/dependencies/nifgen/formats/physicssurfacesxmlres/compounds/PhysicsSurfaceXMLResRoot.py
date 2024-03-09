from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.physicssurfacesxmlres.imports import name_type_map


class PhysicsSurfaceXMLResRoot(MemStruct):

	"""
	# There is an initial 'default' surface, these params are the same as in SurfacePhysicsInfo
	"""

	__name__ = 'PhysicsSurfaceXMLResRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.float_1 = name_type_map['Float'](self.context, 0, None)
		self.float_2 = name_type_map['Float'](self.context, 0, None)
		self.float_3 = name_type_map['Float'](self.context, 0, None)
		self.float_4 = name_type_map['Float'](self.context, 0, None)
		self.unk_64_1 = name_type_map['Uint64'](self.context, 0, None)
		self.count = name_type_map['Ushort'](self.context, 0, None)
		self.short_2 = name_type_map['Ushort'](self.context, 0, None)
		self.unk_32_1 = name_type_map['Uint'](self.context, 0, None)
		self.unk_64_4 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_64_5 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_64_6 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_64_7 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_64_8 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_64_9 = name_type_map['Uint64'](self.context, 0, None)
		self.unk_64_10 = name_type_map['Uint64'](self.context, 0, None)
		self.default_surface_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.name_1 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.name_2 = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.ptr_1 = name_type_map['Pointer'](self.context, 0, name_type_map['EmptyStruct'])
		self.ptr_2 = name_type_map['ArrayPointer'](self.context, self.count, name_type_map['SurfacePhysicsInfo'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'default_surface_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'float_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'float_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'float_3', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'float_4', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unk_64_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'name_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'name_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'ptr_1', name_type_map['Pointer'], (0, name_type_map['EmptyStruct']), (False, None), (None, None)
		yield 'ptr_2', name_type_map['ArrayPointer'], (None, name_type_map['SurfacePhysicsInfo']), (False, None), (None, None)
		yield 'count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'short_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unk_32_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk_64_4', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_64_5', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_64_6', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_64_7', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_64_8', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_64_9', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk_64_10', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'default_surface_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'float_1', name_type_map['Float'], (0, None), (False, None)
		yield 'float_2', name_type_map['Float'], (0, None), (False, None)
		yield 'float_3', name_type_map['Float'], (0, None), (False, None)
		yield 'float_4', name_type_map['Float'], (0, None), (False, None)
		yield 'unk_64_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'name_1', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'name_2', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'ptr_1', name_type_map['Pointer'], (0, name_type_map['EmptyStruct']), (False, None)
		yield 'ptr_2', name_type_map['ArrayPointer'], (instance.count, name_type_map['SurfacePhysicsInfo']), (False, None)
		yield 'count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'short_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unk_32_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk_64_4', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_64_5', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_64_6', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_64_7', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_64_8', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_64_9', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk_64_10', name_type_map['Uint64'], (0, None), (False, None)
