from nifgen.array import Array
from nifgen.formats.bani.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class BanisRoot(MemStruct):

	"""
	40 bytes
	"""

	__name__ = 'BanisRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Uint64'])

		# bytes per bone * num bones
		self.bytes_per_frame = name_type_map['Uint'](self.context, 0, None)

		# how many bytes for each bone per frame
		self.bytes_per_bone = name_type_map['Uint'](self.context, 0, None)

		# Number of frames for all bani files in banis buffer
		self.num_frames = name_type_map['Uint'](self.context, 0, None)

		# number of bones in data, must correspond to ms2
		self.num_bones = name_type_map['Uint'](self.context, 0, None)

		# scale for translation range
		self.loc_scale = name_type_map['Float'](self.context, 0, None)

		# related to minimum of scaled translations, offsets everything ingame the same across all axes
		self.loc_min = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None), (None, None)
		yield 'bytes_per_frame', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bytes_per_bone', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_frames', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'loc_scale', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'loc_min', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zeros', Array, (0, None, (2,), name_type_map['Uint64']), (False, None)
		yield 'bytes_per_frame', name_type_map['Uint'], (0, None), (False, None)
		yield 'bytes_per_bone', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_frames', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'loc_scale', name_type_map['Float'], (0, None), (False, None)
		yield 'loc_min', name_type_map['Float'], (0, None), (False, None)
