from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSEmitter import NiPSEmitter


class NiPSVolumeEmitter(NiPSEmitter):

	"""
	Abstract base class for particle emitters that emit particles from a volume.
	"""

	__name__ = 'NiPSVolumeEmitter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dem_unknown_byte = name_type_map['Byte'](self.context, 0, None)
		self.emitter_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335938816 <= context.version <= 335938816 and context.user_version >= 11, None)
		yield 'emitter_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 335938816 <= instance.context.version <= 335938816 and instance.context.user_version >= 11:
			yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None)
		yield 'emitter_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
