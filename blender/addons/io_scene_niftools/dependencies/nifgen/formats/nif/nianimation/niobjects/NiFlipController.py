from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiFloatInterpController import NiFloatInterpController


class NiFlipController(NiFloatInterpController):

	"""
	Changes the image a Map (TexDesc) will use. Uses a float interpolator to animate the texture index.
	Often used for performing flipbook animation.
	"""

	__name__ = 'NiFlipController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Target texture slot (0=base, 4=glow).
		self.texture_slot = name_type_map['TexType'](self.context, 0, None)
		self.accum_time = name_type_map['Float'](self.context, 0, None)

		# Time between two flips.
		# delta = (start_time - stop_time) / sources.num_indices
		self.delta = name_type_map['Float'](self.context, 0, None)
		self.num_sources = name_type_map['Uint'](self.context, 0, None)

		# The texture sources.
		self.sources = Array(self.context, 0, name_type_map['NiSourceTexture'], (0,), name_type_map['Ref'])

		# The image sources
		self.images = Array(self.context, 0, name_type_map['NiImage'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'texture_slot', name_type_map['TexType'], (0, None), (False, None), (None, None)
		yield 'accum_time', name_type_map['Float'], (0, None), (False, None), (lambda context: 50528269 <= context.version <= 167837799, None)
		yield 'delta', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 167837799, None)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'sources', Array, (0, name_type_map['NiSourceTexture'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'images', Array, (0, name_type_map['NiImage'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version <= 50397184, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'texture_slot', name_type_map['TexType'], (0, None), (False, None)
		if 50528269 <= instance.context.version <= 167837799:
			yield 'accum_time', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version <= 167837799:
			yield 'delta', name_type_map['Float'], (0, None), (False, None)
		yield 'num_sources', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 50528269:
			yield 'sources', Array, (0, name_type_map['NiSourceTexture'], (instance.num_sources,), name_type_map['Ref']), (False, None)
		if instance.context.version <= 50397184:
			yield 'images', Array, (0, name_type_map['NiImage'], (instance.num_sources,), name_type_map['Ref']), (False, None)
