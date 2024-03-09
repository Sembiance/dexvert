from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiInterpolator import NiInterpolator


class BSTreadTransfInterpolator(NiInterpolator):

	"""
	Bethesda-specific interpolator.
	"""

	__name__ = 'BSTreadTransfInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_tread_transforms = name_type_map['Uint'](self.context, 0, None)
		self.tread_transforms = Array(self.context, 0, None, (0,), name_type_map['BSTreadTransform'])
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_tread_transforms', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tread_transforms', Array, (0, None, (None,), name_type_map['BSTreadTransform']), (False, None), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_tread_transforms', name_type_map['Uint'], (0, None), (False, None)
		yield 'tread_transforms', Array, (0, None, (instance.num_tread_transforms,), name_type_map['BSTreadTransform']), (False, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None)
