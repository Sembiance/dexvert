from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiInterpController import NiInterpController


class NiGeomMorpherController(NiInterpController):

	"""
	DEPRECATED (20.5), replaced by NiMorphMeshModifier.
	Time controller for geometry morphing.
	"""

	__name__ = 'NiGeomMorpherController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.morpher_flags = name_type_map['GeomMorpherFlags'](self.context, 0, None)

		# Geometry morphing data index.
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiMorphData'])
		self.always_update = name_type_map['Byte'](self.context, 0, None)
		self.num_interpolators = name_type_map['Uint'](self.context, 0, None)
		self.interpolators = Array(self.context, 0, name_type_map['NiInterpolator'], (0,), name_type_map['Ref'])
		self.interpolator_weights = Array(self.context, 0, None, (0,), name_type_map['MorphWeight'])
		self.num_unknown_ints = name_type_map['Uint'](self.context, 0, None)
		self.unknown_ints = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'morpher_flags', name_type_map['GeomMorpherFlags'], (0, None), (False, None), (lambda context: context.version >= 167772418, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiMorphData']), (False, None), (None, None)
		yield 'always_update', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 67108866, None)
		yield 'num_interpolators', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 167837802, None)
		yield 'interpolators', Array, (0, name_type_map['NiInterpolator'], (None,), name_type_map['Ref']), (False, None), (lambda context: 167837802 <= context.version <= 335544325, None)
		yield 'interpolator_weights', Array, (0, None, (None,), name_type_map['MorphWeight']), (False, None), (lambda context: context.version >= 335609859, None)
		yield 'num_unknown_ints', name_type_map['Uint'], (0, None), (False, None), (lambda context: 167903232 <= context.version <= 335544325 and context.bs_header.bs_version > 9, None)
		yield 'unknown_ints', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: 167903232 <= context.version <= 335544325 and context.bs_header.bs_version > 9, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167772418:
			yield 'morpher_flags', name_type_map['GeomMorpherFlags'], (0, None), (False, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiMorphData']), (False, None)
		if instance.context.version >= 67108866:
			yield 'always_update', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.version >= 167837802:
			yield 'num_interpolators', name_type_map['Uint'], (0, None), (False, None)
		if 167837802 <= instance.context.version <= 335544325:
			yield 'interpolators', Array, (0, name_type_map['NiInterpolator'], (instance.num_interpolators,), name_type_map['Ref']), (False, None)
		if instance.context.version >= 335609859:
			yield 'interpolator_weights', Array, (0, None, (instance.num_interpolators,), name_type_map['MorphWeight']), (False, None)
		if 167903232 <= instance.context.version <= 335544325 and instance.context.bs_header.bs_version > 9:
			yield 'num_unknown_ints', name_type_map['Uint'], (0, None), (False, None)
			yield 'unknown_ints', Array, (0, None, (instance.num_unknown_ints,), name_type_map['Uint']), (False, None)
