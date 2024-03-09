from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiCurve3(BaseStruct):

	"""
	A 3D curve made up of control points and knots.
	"""

	__name__ = 'NiCurve3'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.degree = name_type_map['Uint'](self.context, 0, None)
		self.num_control_points = name_type_map['Uint'](self.context, 0, None)
		self.control_points = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.num_knots = name_type_map['Uint'](self.context, 0, None)
		self.knots = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'degree', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_control_points', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'control_points', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)
		yield 'num_knots', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'knots', Array, (0, None, (None,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'degree', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_control_points', name_type_map['Uint'], (0, None), (False, None)
		yield 'control_points', Array, (0, None, (instance.num_control_points,), name_type_map['Vector3']), (False, None)
		yield 'num_knots', name_type_map['Uint'], (0, None), (False, None)
		yield 'knots', Array, (0, None, (instance.num_knots,), name_type_map['Float']), (False, None)
