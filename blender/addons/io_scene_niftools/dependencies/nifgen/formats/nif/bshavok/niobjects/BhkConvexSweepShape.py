from nifgen.formats.nif.bshavok.niobjects.BhkConvexShapeBase import BhkConvexShapeBase
from nifgen.formats.nif.imports import name_type_map


class BhkConvexSweepShape(BhkConvexShapeBase):

	__name__ = 'bhkConvexSweepShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.shape = name_type_map['Ref'](self.context, 0, name_type_map['BhkConvexShape'])
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		self.radius = name_type_map['Float'](self.context, 0, None)
		self.unknown = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shape', name_type_map['Ref'], (0, name_type_map['BhkConvexShape']), (False, None), (None, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shape', name_type_map['Ref'], (0, name_type_map['BhkConvexShape']), (False, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown', name_type_map['Vector3'], (0, None), (False, None)
