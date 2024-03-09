from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiInterpolator import NiInterpolator


class NiLookAtInterpolator(NiInterpolator):

	"""
	NiLookAtInterpolator rotates an object so that it always faces a target object.
	"""

	__name__ = 'NiLookAtInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['LookAtFlags'](self.context, 0, None)
		self.look_at = name_type_map['Ptr'](self.context, 0, name_type_map['NiNode'])
		self.look_at_name = name_type_map['String'](self.context, 0, None)
		self.transform = name_type_map['NiQuatTransform'](self.context, 0, None)
		self.interpolator_translation = name_type_map['Ref'](self.context, 0, name_type_map['NiPoint3Interpolator'])
		self.interpolator_roll = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatInterpolator'])
		self.interpolator_scale = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatInterpolator'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['LookAtFlags'], (0, None), (False, None), (None, None)
		yield 'look_at', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None), (None, None)
		yield 'look_at_name', name_type_map['String'], (0, None), (False, None), (None, None)
		yield 'transform', name_type_map['NiQuatTransform'], (0, None), (False, None), (lambda context: context.version <= 335806476, None)
		yield 'interpolator_translation', name_type_map['Ref'], (0, name_type_map['NiPoint3Interpolator']), (False, None), (None, None)
		yield 'interpolator_roll', name_type_map['Ref'], (0, name_type_map['NiFloatInterpolator']), (False, None), (None, None)
		yield 'interpolator_scale', name_type_map['Ref'], (0, name_type_map['NiFloatInterpolator']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['LookAtFlags'], (0, None), (False, None)
		yield 'look_at', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None)
		yield 'look_at_name', name_type_map['String'], (0, None), (False, None)
		if instance.context.version <= 335806476:
			yield 'transform', name_type_map['NiQuatTransform'], (0, None), (False, None)
		yield 'interpolator_translation', name_type_map['Ref'], (0, name_type_map['NiPoint3Interpolator']), (False, None)
		yield 'interpolator_roll', name_type_map['Ref'], (0, name_type_map['NiFloatInterpolator']), (False, None)
		yield 'interpolator_scale', name_type_map['Ref'], (0, name_type_map['NiFloatInterpolator']), (False, None)
