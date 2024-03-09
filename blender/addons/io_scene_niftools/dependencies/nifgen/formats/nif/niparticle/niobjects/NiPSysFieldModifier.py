from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysFieldModifier(NiPSysModifier):

	"""
	Base for all force field particle modifiers.
	"""

	__name__ = 'NiPSysFieldModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The object whose position and orientation are the basis of the field.
		self.field_object = name_type_map['Ref'](self.context, 0, name_type_map['NiAVObject'])

		# Magnitude of the force.
		self.magnitude = name_type_map['Float'](self.context, 0, None)

		# How the magnitude diminishes with distance from the Field Object.
		self.attenuation = name_type_map['Float'](self.context, 0, None)

		# Whether or not to use a distance from the Field Object after which there is no effect.
		self.use_max_distance = name_type_map['Bool'](self.context, 0, None)

		# Maximum distance after which there is no effect.
		self.max_distance = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'field_object', name_type_map['Ref'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'magnitude', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'attenuation', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'use_max_distance', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'max_distance', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'field_object', name_type_map['Ref'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'magnitude', name_type_map['Float'], (0, None), (False, None)
		yield 'attenuation', name_type_map['Float'], (0, None), (False, None)
		yield 'use_max_distance', name_type_map['Bool'], (0, None), (False, None)
		yield 'max_distance', name_type_map['Float'], (0, None), (False, None)
