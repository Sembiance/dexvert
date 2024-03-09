from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkShape import BhkShape
from nifgen.formats.nif.imports import name_type_map


class BhkMeshShape(BhkShape):

	"""
	Bethesda extension of hkpMeshShape, but using NiTriStripsData instead of Havok storage.
	Appears in one old Oblivion NIF, but only in certain distributions. NIF version 10.0.1.0 only.
	"""

	__name__ = 'bhkMeshShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_01 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.radius = name_type_map['Float'](self.context, 0, None)
		self.unknown_02 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.scale = name_type_map['Vector4'](self.context, 0, None)
		self.num_shape_properties = name_type_map['Uint'](self.context, 0, None)
		self.shape_properties = Array(self.context, 0, None, (0,), name_type_map['BhkWorldObjCInfoProperty'])
		self.unknown_03 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.num_strips_data = name_type_map['Uint'](self.context, 0, None)
		self.strips_data = Array(self.context, 0, name_type_map['NiTriStripsData'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_01', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_02', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (None, None)
		yield 'scale', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'num_shape_properties', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'shape_properties', Array, (0, None, (None,), name_type_map['BhkWorldObjCInfoProperty']), (False, None), (None, None)
		yield 'unknown_03', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (None, None)
		yield 'num_strips_data', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 167772416, None)
		yield 'strips_data', Array, (0, name_type_map['NiTriStripsData'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version <= 167772416, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_01', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown_02', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
		yield 'scale', name_type_map['Vector4'], (0, None), (False, None)
		yield 'num_shape_properties', name_type_map['Uint'], (0, None), (False, None)
		yield 'shape_properties', Array, (0, None, (instance.num_shape_properties,), name_type_map['BhkWorldObjCInfoProperty']), (False, None)
		yield 'unknown_03', Array, (0, None, (3,), name_type_map['Uint']), (False, None)
		if instance.context.version <= 167772416:
			yield 'num_strips_data', name_type_map['Uint'], (0, None), (False, None)
			yield 'strips_data', Array, (0, name_type_map['NiTriStripsData'], (instance.num_strips_data,), name_type_map['Ref']), (False, None)
