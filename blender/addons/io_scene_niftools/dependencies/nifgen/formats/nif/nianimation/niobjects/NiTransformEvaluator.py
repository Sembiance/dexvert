from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiKeyBasedEvaluator import NiKeyBasedEvaluator


class NiTransformEvaluator(NiKeyBasedEvaluator):

	__name__ = 'NiTransformEvaluator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = name_type_map['NiQuatTransform'](self.context, 0, None)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiTransformData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['NiQuatTransform'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiTransformData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['NiQuatTransform'], (0, None), (False, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiTransformData']), (False, None)
