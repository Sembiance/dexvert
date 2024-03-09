from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BSInvMarker(NiExtraData):

	"""
	Orientation marker for Skyrim's inventory view.
	How to show the nif in the player's inventory.
	Typically attached to the root node of the nif tree.
	If not present, then Skyrim will still show the nif in inventory,
	using the default values.
	Name should be 'INV' (without the quotes).
	For rotations, a short of "4712" appears as "4.712" but "959" appears as "0.959"  meshes\weapons\daedric\daedricbowskinned.nif
	"""

	__name__ = 'BSInvMarker'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.rotation_x = name_type_map['Ushort'].from_value(0)
		self.rotation_y = name_type_map['Ushort'].from_value(0)
		self.rotation_z = name_type_map['Ushort'].from_value(0)

		# Zoom factor.
		self.zoom = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'rotation_x', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'rotation_y', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'rotation_z', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'zoom', name_type_map['Float'], (0, None), (False, 1.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'rotation_x', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'rotation_y', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'rotation_z', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'zoom', name_type_map['Float'], (0, None), (False, 1.0)
