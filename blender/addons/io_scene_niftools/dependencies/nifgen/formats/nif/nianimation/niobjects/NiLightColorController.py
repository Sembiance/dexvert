from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiPoint3InterpController import NiPoint3InterpController


class NiLightColorController(NiPoint3InterpController):

	"""
	Animates the ambient, diffuse and specular colors of an NiLight.
	NiInterpController::GetCtlrID() string formats:
	['Diffuse', 'Ambient'] (Depending on "Target Color")
	"""

	__name__ = 'NiLightColorController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.target_color = name_type_map['LightColor'](self.context, 0, None)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiPosData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target_color', name_type_map['LightColor'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiPosData']), (False, None), (lambda context: context.version <= 167837799, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837696:
			yield 'target_color', name_type_map['LightColor'], (0, None), (False, None)
		if instance.context.version <= 167837799:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiPosData']), (False, None)
