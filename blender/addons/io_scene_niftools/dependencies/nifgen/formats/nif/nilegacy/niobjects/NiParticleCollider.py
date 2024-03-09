from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleModifier import NiParticleModifier


class NiParticleCollider(NiParticleModifier):

	__name__ = 'NiParticleCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bounce = name_type_map['Float'](self.context, 0, None)
		self.spawn_on_collide = name_type_map['Bool'](self.context, 0, None)
		self.die_on_collide = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounce', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'spawn_on_collide', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 67239938, None)
		yield 'die_on_collide', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 67239938, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bounce', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 67239938:
			yield 'spawn_on_collide', name_type_map['Bool'], (0, None), (False, None)
			yield 'die_on_collide', name_type_map['Bool'], (0, None), (False, None)
