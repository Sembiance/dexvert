from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiInterpController import NiInterpController


class NiMorphWeightsController(NiInterpController):

	"""
	Manipulates a mesh with the semantic MORPHWEIGHTS using an NiMorphMeshModifier.
	"""

	__name__ = 'NiMorphWeightsController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count = name_type_map['Uint'](self.context, 0, None)
		self.num_interpolators = name_type_map['Uint'](self.context, 0, None)
		self.interpolators = Array(self.context, 0, name_type_map['NiInterpolator'], (0,), name_type_map['Ref'])
		self.num_targets = name_type_map['Uint'](self.context, 0, None)
		self.target_names = Array(self.context, 0, None, (0,), name_type_map['NiFixedString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_interpolators', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'interpolators', Array, (0, name_type_map['NiInterpolator'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_targets', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'target_names', Array, (0, None, (None,), name_type_map['NiFixedString']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'count', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_interpolators', name_type_map['Uint'], (0, None), (False, None)
		yield 'interpolators', Array, (0, name_type_map['NiInterpolator'], (instance.num_interpolators,), name_type_map['Ref']), (False, None)
		yield 'num_targets', name_type_map['Uint'], (0, None), (False, None)
		yield 'target_names', Array, (0, None, (instance.num_targets,), name_type_map['NiFixedString']), (False, None)
