from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BSAnimNotes(NiObject):

	"""
	Bethesda-specific object.
	"""

	__name__ = 'BSAnimNotes'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of BSAnimNote objects.
		self.num_anim_notes = name_type_map['Ushort'](self.context, 0, None)

		# BSAnimNote objects.
		self.anim_notes = Array(self.context, 0, name_type_map['BSAnimNote'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_anim_notes', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'anim_notes', Array, (0, name_type_map['BSAnimNote'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_anim_notes', name_type_map['Ushort'], (0, None), (False, None)
		yield 'anim_notes', Array, (0, name_type_map['BSAnimNote'], (instance.num_anim_notes,), name_type_map['Ref']), (False, None)
