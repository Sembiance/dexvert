from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BSAnimNote(NiObject):

	"""
	Bethesda-specific object.
	"""

	__name__ = 'BSAnimNote'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Type of this note.
		self.type = name_type_map['AnimNoteType'](self.context, 0, None)

		# Location in time.
		self.time = name_type_map['Float'](self.context, 0, None)
		self.arm = name_type_map['Uint'](self.context, 0, None)
		self.gain = name_type_map['Float'](self.context, 0, None)
		self.state = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'type', name_type_map['AnimNoteType'], (0, None), (False, None), (None, None)
		yield 'time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'arm', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'gain', name_type_map['Float'], (0, None), (False, None), (None, True)
		yield 'state', name_type_map['Uint'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'type', name_type_map['AnimNoteType'], (0, None), (False, None)
		yield 'time', name_type_map['Float'], (0, None), (False, None)
		if instance.type == 1:
			yield 'arm', name_type_map['Uint'], (0, None), (False, None)
		if instance.type == 2:
			yield 'gain', name_type_map['Float'], (0, None), (False, None)
			yield 'state', name_type_map['Uint'], (0, None), (False, None)
