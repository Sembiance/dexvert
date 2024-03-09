from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class NiRoomGroup(NiNode):

	"""
	NiRoomGroup represents a set of connected rooms i.e. a game level.
	"""

	__name__ = 'NiRoomGroup'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Object that represents the room group as seen from the outside.
		self.shell = name_type_map['Ptr'](self.context, 0, name_type_map['NiNode'])
		self.num_rooms = name_type_map['Uint'](self.context, 0, None)
		self.rooms = Array(self.context, 0, name_type_map['NiRoom'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shell', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None), (None, None)
		yield 'num_rooms', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'rooms', Array, (0, name_type_map['NiRoom'], (None,), name_type_map['Ptr']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shell', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None)
		yield 'num_rooms', name_type_map['Uint'], (0, None), (False, None)
		yield 'rooms', Array, (0, name_type_map['NiRoom'], (instance.num_rooms,), name_type_map['Ptr']), (False, None)
