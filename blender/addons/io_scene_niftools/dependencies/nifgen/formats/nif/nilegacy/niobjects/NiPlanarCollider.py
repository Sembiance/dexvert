from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleCollider import NiParticleCollider


class NiPlanarCollider(NiParticleCollider):

	"""
	LEGACY (pre-10.1) particle modifier.
	"""

	__name__ = 'NiPlanarCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.height = name_type_map['Float'](self.context, 0, None)
		self.width = name_type_map['Float'](self.context, 0, None)
		self.position = name_type_map['Vector3'](self.context, 0, None)
		self.x_vector = name_type_map['Vector3'](self.context, 0, None)
		self.y_vector = name_type_map['Vector3'](self.context, 0, None)
		self.plane = name_type_map['NiPlane'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'height', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'width', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'x_vector', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'y_vector', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'plane', name_type_map['NiPlane'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'height', name_type_map['Float'], (0, None), (False, None)
		yield 'width', name_type_map['Float'], (0, None), (False, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None)
		yield 'x_vector', name_type_map['Vector3'], (0, None), (False, None)
		yield 'y_vector', name_type_map['Vector3'], (0, None), (False, None)
		yield 'plane', name_type_map['NiPlane'], (0, None), (False, None)
