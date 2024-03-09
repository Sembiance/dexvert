from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiPoint3InterpController import NiPoint3InterpController


class NiMaterialColorController(NiPoint3InterpController):

	"""
	Time controller for material color. Flags are used for color selection in versions below 10.1.0.0.
	Bits 4-5: Target Color (00 = Ambient, 01 = Diffuse, 10 = Specular, 11 = Emissive)
	NiInterpController::GetCtlrID() string formats:
	['AMB', 'DIFF', 'SPEC', 'SELF_ILLUM'] (Depending on "Target Color")
	"""

	__name__ = 'NiMaterialColorController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Selects which color to control.
		self.target_color = name_type_map['MaterialColor'](self.context, 0, None)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiPosData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target_color', name_type_map['MaterialColor'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiPosData']), (False, None), (lambda context: context.version <= 167837799, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837696:
			yield 'target_color', name_type_map['MaterialColor'], (0, None), (False, None)
		if instance.context.version <= 167837799:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiPosData']), (False, None)
	def get_target_color(self):
		"""Get target color (works for all nif versions)."""
		return ((self.flags >> 4) & 7) | self.target_color

	def set_target_color(self, target_color):
		"""Set target color (works for all nif versions)."""
		self.flags |= (target_color & 7) << 4
		self.target_color = target_color


