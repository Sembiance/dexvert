from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObjectPalette import NiAVObjectPalette


class NiDefaultAVObjectPalette(NiAVObjectPalette):

	"""
	NiAVObjectPalette implementation. Used to quickly look up objects by name.
	"""

	__name__ = 'NiDefaultAVObjectPalette'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Scene root of the object palette.
		self.scene = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])

		# Number of objects.
		self.num_objs = name_type_map['Uint'](self.context, 0, None)

		# The objects.
		self.objs = Array(self.context, 0, None, (0,), name_type_map['AVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'scene', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'num_objs', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'objs', Array, (0, None, (None,), name_type_map['AVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'scene', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'num_objs', name_type_map['Uint'], (0, None), (False, None)
		yield 'objs', Array, (0, None, (instance.num_objs,), name_type_map['AVObject']), (False, None)
