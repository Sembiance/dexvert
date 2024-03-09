import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class ControlledBlock(BaseStruct):

	"""
	In a .kf file, this links to a controllable object, via its name (or for version 10.2.0.0 and up, a link and offset to a NiStringPalette that contains the name), and a sequence of interpolators that apply to this controllable object, via links.
	For Controller ID, NiInterpController::GetCtlrID() virtual function returns a string formatted specifically for the derived type.
	For Interpolator ID, NiInterpController::GetInterpolatorID() virtual function returns a string formatted specifically for the derived type.
	The string formats are documented on the relevant niobject blocks.
	"""

	__name__ = 'ControlledBlock'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Name of a controllable object in another NIF file.
		self.target_name = name_type_map['SizedString'](self.context, 0, None)
		self.interpolator = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])
		self.controller = name_type_map['Ref'](self.context, 0, name_type_map['NiTimeController'])
		self.blend_interpolator = name_type_map['Ref'](self.context, 0, name_type_map['NiBlendInterpolator'])
		self.blend_index = name_type_map['Ushort'](self.context, 0, None)

		# Idle animations tend to have low values for this, and high values tend to correspond with the important parts of the animations.
		self.priority = name_type_map['Byte'](self.context, 0, None)

		# The name of the animated NiAVObject.
		self.node_name = name_type_map['String'](self.context, 0, None)

		# The RTTI type of the NiProperty the controller is attached to, if applicable.
		self.property_type = name_type_map['String'](self.context, 0, None)

		# The RTTI type of the NiTimeController.
		self.controller_type = name_type_map['String'](self.context, 0, None)

		# An ID that can uniquely identify the controller among others of the same type on the same NiObjectNET.
		self.controller_id = name_type_map['String'](self.context, 0, None)

		# An ID that can uniquely identify the interpolator among others of the same type on the same NiObjectNET.
		self.interpolator_id = name_type_map['String'](self.context, 0, None)

		# Refers to the NiStringPalette which contains the name of the controlled NIF object.
		self.string_palette = name_type_map['Ref'](self.context, 0, name_type_map['NiStringPalette'])

		# Offset in NiStringPalette to the name of the animated NiAVObject.
		self.node_name_offset = name_type_map['StringOffset'](self.context, 0, None)

		# Offset in NiStringPalette to the RTTI type of the NiProperty the controller is attached to, if applicable.
		self.property_type_offset = name_type_map['StringOffset'](self.context, 0, None)

		# Offset in NiStringPalette to the RTTI type of the NiTimeController.
		self.controller_type_offset = name_type_map['StringOffset'](self.context, 0, None)

		# Offset in NiStringPalette to an ID that can uniquely identify the controller among others of the same type on the same NiObjectNET.
		self.controller_id_offset = name_type_map['StringOffset'](self.context, 0, None)

		# Offset in NiStringPalette to an ID that can uniquely identify the interpolator among others of the same type on the same NiObjectNET.
		self.interpolator_id_offset = name_type_map['StringOffset'](self.context, 0, None)

		# The name of the animated NiAVObject.
		self.node_name = name_type_map['String'](self.context, 0, None)

		# The RTTI type of the NiProperty the controller is attached to, if applicable.
		self.property_type = name_type_map['String'](self.context, 0, None)

		# The RTTI type of the NiTimeController.
		self.controller_type = name_type_map['String'](self.context, 0, None)

		# An ID that can uniquely identify the controller among others of the same type on the same NiObjectNET.
		self.controller_id = name_type_map['String'](self.context, 0, None)

		# An ID that can uniquely identify the interpolator among others of the same type on the same NiObjectNET.
		self.interpolator_id = name_type_map['String'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target_name', name_type_map['SizedString'], (0, None), (False, None), (lambda context: context.version <= 167837799, None)
		yield 'interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (lambda context: context.version >= 167837802, None)
		yield 'controller', name_type_map['Ref'], (0, name_type_map['NiTimeController']), (False, None), (lambda context: context.version <= 335872000, None)
		yield 'blend_interpolator', name_type_map['Ref'], (0, name_type_map['NiBlendInterpolator']), (False, None), (lambda context: 167837800 <= context.version <= 167837806, None)
		yield 'blend_index', name_type_map['Ushort'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 167837806, None)
		yield 'priority', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 167837802 and context.bs_header.bs_version > 0, None)
		yield 'node_name', name_type_map['String'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 167837809, None)
		yield 'property_type', name_type_map['String'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 167837809, None)
		yield 'controller_type', name_type_map['String'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 167837809, None)
		yield 'controller_id', name_type_map['String'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 167837809, None)
		yield 'interpolator_id', name_type_map['String'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 167837809, None)
		yield 'string_palette', name_type_map['Ref'], (0, name_type_map['NiStringPalette']), (False, None), (lambda context: 167903232 <= context.version <= 335609856, None)
		yield 'node_name_offset', name_type_map['StringOffset'], (0, None), (False, None), (lambda context: 167903232 <= context.version <= 335609856, None)
		yield 'property_type_offset', name_type_map['StringOffset'], (0, None), (False, None), (lambda context: 167903232 <= context.version <= 335609856, None)
		yield 'controller_type_offset', name_type_map['StringOffset'], (0, None), (False, None), (lambda context: 167903232 <= context.version <= 335609856, None)
		yield 'controller_id_offset', name_type_map['StringOffset'], (0, None), (False, None), (lambda context: 167903232 <= context.version <= 335609856, None)
		yield 'interpolator_id_offset', name_type_map['StringOffset'], (0, None), (False, None), (lambda context: 167903232 <= context.version <= 335609856, None)
		yield 'node_name', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 335609857, None)
		yield 'property_type', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 335609857, None)
		yield 'controller_type', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 335609857, None)
		yield 'controller_id', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 335609857, None)
		yield 'interpolator_id', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 335609857, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167837799:
			yield 'target_name', name_type_map['SizedString'], (0, None), (False, None)
		if instance.context.version >= 167837802:
			yield 'interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		if instance.context.version <= 335872000:
			yield 'controller', name_type_map['Ref'], (0, name_type_map['NiTimeController']), (False, None)
		if 167837800 <= instance.context.version <= 167837806:
			yield 'blend_interpolator', name_type_map['Ref'], (0, name_type_map['NiBlendInterpolator']), (False, None)
			yield 'blend_index', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 167837802 and instance.context.bs_header.bs_version > 0:
			yield 'priority', name_type_map['Byte'], (0, None), (False, None)
		if 167837800 <= instance.context.version <= 167837809:
			yield 'node_name', name_type_map['String'], (0, None), (False, None)
			yield 'property_type', name_type_map['String'], (0, None), (False, None)
			yield 'controller_type', name_type_map['String'], (0, None), (False, None)
			yield 'controller_id', name_type_map['String'], (0, None), (False, None)
			yield 'interpolator_id', name_type_map['String'], (0, None), (False, None)
		if 167903232 <= instance.context.version <= 335609856:
			yield 'string_palette', name_type_map['Ref'], (0, name_type_map['NiStringPalette']), (False, None)
			yield 'node_name_offset', name_type_map['StringOffset'], (0, None), (False, None)
			yield 'property_type_offset', name_type_map['StringOffset'], (0, None), (False, None)
			yield 'controller_type_offset', name_type_map['StringOffset'], (0, None), (False, None)
			yield 'controller_id_offset', name_type_map['StringOffset'], (0, None), (False, None)
			yield 'interpolator_id_offset', name_type_map['StringOffset'], (0, None), (False, None)
		if instance.context.version >= 335609857:
			yield 'node_name', name_type_map['String'], (0, None), (False, None)
			yield 'property_type', name_type_map['String'], (0, None), (False, None)
			yield 'controller_type', name_type_map['String'], (0, None), (False, None)
			yield 'controller_id', name_type_map['String'], (0, None), (False, None)
			yield 'interpolator_id', name_type_map['String'], (0, None), (False, None)


	"""
	[TODO] Adjust for new field names in xml.
	>>> from pyffi.formats.nif import NifFormat
	>>> link = NifFormat.ControlledBlock()
	>>> link.node_name_offset
	-1
	>>> link.set_node_name("Bip01")
	>>> link.node_name_offset
	0
	>>> link.get_node_name()
	'Bip01'
	>>> link.node_name
	'Bip01'
	>>> link.set_node_name("Bip01 Tail")
	>>> link.node_name_offset
	6
	>>> link.get_node_name()
	'Bip01 Tail'
	>>> link.node_name
	'Bip01 Tail'
	"""
	def _get_string(self, offset):
		"""A wrapper around string_palette.palette.get_string. Used by get_node_name
		etc. Returns the string at given offset."""
		if offset == -1:
			return ''

		if not self.string_palette:
			return ''

		return self.string_palette.palette.get_string(offset)

	def _add_string(self, text):
		"""Wrapper for string_palette.palette.add_string. Used by set_node_name etc.
		Returns offset of string added."""
		# create string palette if none exists yet
		if not self.string_palette:
			self.string_palette = NifFormat.classes.NiStringPalette(self.context)
		# add the string and return the offset
		return self.string_palette.palette.add_string(text)

	def get_node_name(self):
		"""Return the node name.

		>>> # a doctest
		>>> from pyffi.formats.nif import NifFormat
		>>> link = NifFormat.ControllerLink()
		>>> link.string_palette = NifFormat.NiStringPalette()
		>>> palette = link.string_palette.palette
		>>> link.node_name_offset = palette.add_string("Bip01")
		>>> link.get_node_name()
		'Bip01'

		>>> # another doctest
		>>> from pyffi.formats.nif import NifFormat
		>>> link = NifFormat.ControllerLink()
		>>> link.node_name = "Bip01"
		>>> link.get_node_name()
		'Bip01'
		"""
		# eg. ZT2
		if self.target_name:
			return self.target_name
		# eg. Fallout
		elif self.node_name:
			return self.node_name
		# eg. Loki (StringPalette)
		else:
			return self._get_string(self.node_name_offset)

	def set_node_name(self, text):
		self.target_name = text
		self.node_name = text
		self.node_name_offset = self._add_string(text)

	def get_property_type(self):
		if self.property_type:
			return self.property_type
		else:
			return self._get_string(self.property_type_offset)

	def set_property_type(self, text):
		self.property_type = text
		self.property_type_offset = self._add_string(text)

	def get_controller_type(self):
		if self.controller_type:
			return self.controller_type
		else:
			return self._get_string(self.controller_type_offset)

	def set_controller_type(self, text):
		self.controller_type = text
		self.controller_type_offset = self._add_string(text)

	def get_variable_1(self):
		if self.variable_1:
			return self.variable_1
		else:
			return self._get_string(self.variable_1_offset)

	def set_variable_1(self, text):
		self.variable_1 = text
		self.variable_1_offset = self._add_string(text)

	def get_variable_2(self):
		if self.variable_2:
			return self.variable_2
		else:
			return self._get_string(self.variable_2_offset)

	def set_variable_2(self, text):
		self.variable_2 = text
		self.variable_2_offset = self._add_string(text)

