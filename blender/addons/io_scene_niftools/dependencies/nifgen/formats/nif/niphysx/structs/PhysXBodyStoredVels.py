from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class PhysXBodyStoredVels(BaseStruct):

	__name__ = 'PhysXBodyStoredVels'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.linear_velocity = name_type_map['Vector3'](self.context, 0, None)
		self.angular_velocity = name_type_map['Vector3'](self.context, 0, None)
		self.sleep = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'linear_velocity', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'angular_velocity', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'sleep', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 503447555, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'linear_velocity', name_type_map['Vector3'], (0, None), (False, None)
		yield 'angular_velocity', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version >= 503447555:
			yield 'sleep', name_type_map['Bool'], (0, None), (False, None)
