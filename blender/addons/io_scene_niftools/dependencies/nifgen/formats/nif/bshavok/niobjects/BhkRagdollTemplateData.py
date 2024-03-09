from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BhkRagdollTemplateData(NiObject):

	"""
	Data for bhkRagdollTemplate
	"""

	__name__ = 'bhkRagdollTemplateData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['NiFixedString'](self.context, 0, None)
		self.mass = name_type_map['Float'].from_value(9.0)
		self.restitution = name_type_map['Float'].from_value(0.8)
		self.friction = name_type_map['Float'].from_value(0.3)
		self.radius = name_type_map['Float'].from_value(1.0)
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		self.num_constraints = name_type_map['Uint'](self.context, 0, None)
		self.constraint = Array(self.context, 0, None, (0,), name_type_map['BhkWrappedConstraintData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, 9.0), (None, None)
		yield 'restitution', name_type_map['Float'], (0, None), (False, 0.8), (None, None)
		yield 'friction', name_type_map['Float'], (0, None), (False, 0.3), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)
		yield 'num_constraints', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'constraint', Array, (0, None, (None,), name_type_map['BhkWrappedConstraintData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, 9.0)
		yield 'restitution', name_type_map['Float'], (0, None), (False, 0.8)
		yield 'friction', name_type_map['Float'], (0, None), (False, 0.3)
		yield 'radius', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
		yield 'num_constraints', name_type_map['Uint'], (0, None), (False, None)
		yield 'constraint', Array, (0, None, (instance.num_constraints,), name_type_map['BhkWrappedConstraintData']), (False, None)
