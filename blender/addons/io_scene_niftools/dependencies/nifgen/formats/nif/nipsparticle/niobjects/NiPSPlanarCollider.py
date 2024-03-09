from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSCollider import NiPSCollider


class NiPSPlanarCollider(NiPSCollider):

	"""
	A planar collider for particles.
	"""

	__name__ = 'NiPSPlanarCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.width = name_type_map['Float'].from_value(1.0)
		self.height = name_type_map['Float'].from_value(1.0)
		self.x_axis = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		self.y_axis = name_type_map['Vector3'].from_value((0.0, 1.0, 0.0))
		self.collider_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'width', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'height', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'x_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)
		yield 'y_axis', name_type_map['Vector3'], (0, None), (False, (0.0, 1.0, 0.0)), (None, None)
		yield 'collider_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'width', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'height', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'x_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
		yield 'y_axis', name_type_map['Vector3'], (0, None), (False, (0.0, 1.0, 0.0))
		yield 'collider_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
