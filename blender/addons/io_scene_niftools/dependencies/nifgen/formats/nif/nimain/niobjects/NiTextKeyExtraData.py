from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class NiTextKeyExtraData(NiExtraData):

	"""
	Extra data that holds an array of NiTextKey objects for use in animation sequences.
	"""

	__name__ = 'NiTextKeyExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The number of text keys that follow.
		self.num_text_keys = name_type_map['Uint'](self.context, 0, None)

		# List of textual notes and at which time they take effect. Used for designating the start and stop of animations and the triggering of sounds.
		self.text_keys = Array(self.context, 1, name_type_map['String'], (0,), name_type_map['Key'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_text_keys', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'text_keys', Array, (1, name_type_map['String'], (None,), name_type_map['Key']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_text_keys', name_type_map['Uint'], (0, None), (False, None)
		yield 'text_keys', Array, (1, name_type_map['String'], (instance.num_text_keys,), name_type_map['Key']), (False, None)
