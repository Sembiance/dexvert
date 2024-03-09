from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class BSLagBoneController(NiTimeController):

	"""
	A controller that trails a bone behind an actor.
	"""

	__name__ = 'BSLagBoneController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# How long it takes to rotate about an actor back to rest position.
		self.linear_velocity = name_type_map['Float'].from_value(3.0)

		# How the bone lags rotation
		self.linear_rotation = name_type_map['Float'].from_value(1.0)

		# How far bone will tail an actor.
		self.maximum_distance = name_type_map['Float'].from_value(400.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'linear_velocity', name_type_map['Float'], (0, None), (False, 3.0), (None, None)
		yield 'linear_rotation', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'maximum_distance', name_type_map['Float'], (0, None), (False, 400.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'linear_velocity', name_type_map['Float'], (0, None), (False, 3.0)
		yield 'linear_rotation', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'maximum_distance', name_type_map['Float'], (0, None), (False, 400.0)
