import struct

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Footer(BaseStruct):

	"""
	The NIF file footer.
	"""

	__name__ = 'Footer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The number of root references.
		self.num_roots = name_type_map['Uint'](self.context, 0, None)

		# List of root NIF objects. If there is a camera, for 1st person view, then this NIF object is referred to as well in this list, even if it is not a root object (usually we want the camera to be attached to the Bip Head node).
		self.roots = Array(self.context, 0, name_type_map['NiObject'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_roots', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'roots', Array, (0, name_type_map['NiObject'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 50528269, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 50528269:
			yield 'num_roots', name_type_map['Uint'], (0, None), (False, None)
			yield 'roots', Array, (0, name_type_map['NiObject'], (instance.num_roots,), name_type_map['Ref']), (False, None)

	@classmethod
	def from_stream(cls, stream, context, arg=0, template=None):
		instance = super().from_stream(stream, context, arg, template)
		modification = getattr(context, "modification", None)
		if modification == "neosteam":
			extrabyte, = struct.unpack("<B", stream.read(1))
			if extrabyte != 0:
				raise ValueError(f"Expected trailing zero byte in footer, but got {extrabyte} instead.")
		instance.io_size = stream.tell() - instance.io_start
		return instance

	@classmethod
	def to_stream(cls, instance, stream, context, arg=0, template=None):
		super().to_stream(instance, stream, context, arg, template)
		modification = getattr(instance.context, "modification", None)
		if modification == "neosteam":
			stream.write("\x00".encode("ascii"))
		return instance
