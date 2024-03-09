from nifgen.formats.ovl.compounds.Triplet import Triplet


from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class MimeEntry(BaseStruct):

	"""
	Description of one mime type or file class.
	Inside the archive not the stored mime hash is used but the extension hash, has to be generated, eg. djb2("bani") == 2090104799
	"""

	__name__ = 'MimeEntry'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['OffsetString'](self.context, self.context.names, None)
		self.zero_0 = name_type_map['Uint'].from_value(0)

		# hash of this mime, changes with mime version; not used anywhere else in the ovl
		self.mime_hash = name_type_map['Uint'](self.context, 0, None)

		# usually increments with game
		self.mime_version = name_type_map['Uint'](self.context, 0, None)

		# Id of this class type. Later in the file there is a reference to this Id; offset into FileEntry list in number of files
		self.file_index_offset = name_type_map['Uint'](self.context, 0, None)

		# Number of entries of this class in the file.; from 'file index offset', this many files belong to this file extension
		self.file_count = name_type_map['Uint'](self.context, 0, None)
		self.zero_1 = name_type_map['Uint'](self.context, 0, None)

		# constant per mime, grab this many triplets
		self.triplet_count = name_type_map['Uint'](self.context, 0, None)

		# index into triplets list
		self.triplet_offset = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'zero_0', name_type_map['Uint'], (0, None), (False, 0), (None, None)
		yield 'mime_hash', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 18, None)
		yield 'mime_version', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'file_index_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'file_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 17, None)
		yield 'triplet_count', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 20, None)
		yield 'triplet_offset', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 20, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['OffsetString'], (instance.context.names, None), (False, None)
		yield 'zero_0', name_type_map['Uint'], (0, None), (False, 0)
		if instance.context.version >= 18:
			yield 'mime_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'mime_version', name_type_map['Uint'], (0, None), (False, None)
		yield 'file_index_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'file_count', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 17:
			yield 'zero_1', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 20:
			yield 'triplet_count', name_type_map['Uint'], (0, None), (False, None)
			yield 'triplet_offset', name_type_map['Uint'], (0, None), (False, None)

	def update_constants(self, ovl):
		"""Update the constants"""
		self.name = ovl.get_mime(self.ext, "name")
		self.mime_hash = ovl.get_mime(self.ext, "hash")
		self.mime_version = ovl.get_mime(self.ext, "version")
		triplet_grab = ovl.get_mime(self.ext, "triplets")
		self.triplet_offset = len(ovl.triplets)
		self.triplet_count = len(triplet_grab)
		for triplet in triplet_grab:
			trip = Triplet(self.context)
			trip.a, trip.b, trip.c = triplet
			ovl.triplets.append(trip)

