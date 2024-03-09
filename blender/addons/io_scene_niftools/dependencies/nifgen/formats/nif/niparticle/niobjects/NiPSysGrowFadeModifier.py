from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysGrowFadeModifier(NiPSysModifier):

	"""
	Particle modifier that controls the time it takes to grow and shrink a particle.
	"""

	__name__ = 'NiPSysGrowFadeModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The time taken to grow from 0 to their specified size.
		self.grow_time = name_type_map['Float'](self.context, 0, None)

		# Specifies the particle generation to which the grow effect should be applied. This is usually generation 0, so that newly created particles will grow.
		self.grow_generation = name_type_map['Ushort'](self.context, 0, None)

		# The time taken to shrink from their specified size to 0.
		self.fade_time = name_type_map['Float'](self.context, 0, None)

		# Specifies the particle generation to which the shrink effect should be applied. This is usually the highest supported generation for the particle system.
		self.fade_generation = name_type_map['Ushort'](self.context, 0, None)

		# A multiplier on the base particle scale.
		self.base_scale = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'grow_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'grow_generation', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'fade_time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'fade_generation', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'base_scale', name_type_map['Float'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version >= 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'grow_time', name_type_map['Float'], (0, None), (False, None)
		yield 'grow_generation', name_type_map['Ushort'], (0, None), (False, None)
		yield 'fade_time', name_type_map['Float'], (0, None), (False, None)
		yield 'fade_generation', name_type_map['Ushort'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version >= 34:
			yield 'base_scale', name_type_map['Float'], (0, None), (False, None)
