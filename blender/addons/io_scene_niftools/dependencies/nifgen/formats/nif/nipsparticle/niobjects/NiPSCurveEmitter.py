from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSEmitter import NiPSEmitter


class NiPSCurveEmitter(NiPSEmitter):

	"""
	Emits particles from a curve.
	"""

	__name__ = 'NiPSCurveEmitter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.has_curve = name_type_map['Bool'](self.context, 0, None)
		self.curve = name_type_map['NiCurve3'](self.context, 0, None)
		self.curve_parent = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		self.emitter_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_curve', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'curve', name_type_map['NiCurve3'], (0, None), (False, None), (None, True)
		yield 'curve_parent', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'emitter_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'has_curve', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_curve:
			yield 'curve', name_type_map['NiCurve3'], (0, None), (False, None)
		yield 'curve_parent', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'emitter_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
