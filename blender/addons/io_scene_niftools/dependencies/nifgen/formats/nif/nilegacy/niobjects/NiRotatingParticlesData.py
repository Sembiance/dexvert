from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiParticlesData import NiParticlesData


class NiRotatingParticlesData(NiParticlesData):

	"""
	Rotating particles data object.
	"""

	__name__ = 'NiRotatingParticlesData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Is the particle rotation array present?
		self.has_rotations_2 = name_type_map['Bool'](self.context, 0, None)

		# The individual particle rotations.
		self.rotations_2 = Array(self.context, 0, None, (0,), name_type_map['Quaternion'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_rotations_2', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 67240448, None)
		yield 'rotations_2', Array, (0, None, (None,), name_type_map['Quaternion']), (False, None), (lambda context: context.version <= 67240448, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 67240448:
			yield 'has_rotations_2', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 67240448 and instance.has_rotations_2:
			yield 'rotations_2', Array, (0, None, (instance.num_vertices,), name_type_map['Quaternion']), (False, None)
