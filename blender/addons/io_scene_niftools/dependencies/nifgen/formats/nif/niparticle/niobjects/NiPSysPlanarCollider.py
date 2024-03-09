from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysCollider import NiPSysCollider


class NiPSysPlanarCollider(NiPSysCollider):

	"""
	Particle Collider object which particles will interact with.
	"""

	__name__ = 'NiPSysPlanarCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Width of the plane along the X Axis.
		self.width = name_type_map['Float'](self.context, 0, None)

		# Height of the plane along the Y Axis.
		self.height = name_type_map['Float'](self.context, 0, None)

		# Axis defining a plane, relative to Collider Object.
		self.x_axis = name_type_map['Vector3'](self.context, 0, None)

		# Axis defining a plane, relative to Collider Object.
		self.y_axis = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'width', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'height', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'x_axis', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'y_axis', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'width', name_type_map['Float'], (0, None), (False, None)
		yield 'height', name_type_map['Float'], (0, None), (False, None)
		yield 'x_axis', name_type_map['Vector3'], (0, None), (False, None)
		yield 'y_axis', name_type_map['Vector3'], (0, None), (False, None)
