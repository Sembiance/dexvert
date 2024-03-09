from nifgen.formats.nif.nimain.niobjects.NiIntegerExtraData import NiIntegerExtraData


class BSXFlags(NiIntegerExtraData):

	"""
	Controls animation and collision.  Integer holds flags:
	Bit 0 : enable havok, bAnimated(Skyrim)
	Bit 1 : enable collision, bHavok(Skyrim)
	Bit 2 : is skeleton nif?, bRagdoll(Skyrim)
	Bit 3 : enable animation, bComplex(Skyrim)
	Bit 4 : FlameNodes present, bAddon(Skyrim)
	Bit 5 : EditorMarkers present, bEditorMarker(Skyrim)
	Bit 6 : bDynamic(Skyrim)
	Bit 7 : bArticulated(Skyrim)
	Bit 8 : bIKTarget(Skyrim)/needsTransformUpdates
	Bit 9 : bExternalEmit(Skyrim)
	Bit 10: bMagicShaderParticles(Skyrim)
	Bit 11: bLights(Skyrim)
	Bit 12: bBreakable(Skyrim)
	Bit 13: bSearchedBreakable(Skyrim) .. Runtime only?
	"""

	__name__ = 'BSXFlags'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
