from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSForce import NiPSForce


class NiPSDragForce(NiPSForce):

	"""
	Applies a linear drag force to particles.
	"""

	__name__ = 'NiPSDragForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.drag_axis = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		self.percentage = name_type_map['Float'].from_value(0.05)
		self.range = name_type_map['Float'].from_value(3.402823466e+38)
		self.range_falloff = name_type_map['Float'].from_value(3.402823466e+38)
		self.drag_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'drag_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)
		yield 'percentage', name_type_map['Float'], (0, None), (False, 0.05), (None, None)
		yield 'range', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'range_falloff', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'drag_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'drag_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
		yield 'percentage', name_type_map['Float'], (0, None), (False, 0.05)
		yield 'range', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'range_falloff', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'drag_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
