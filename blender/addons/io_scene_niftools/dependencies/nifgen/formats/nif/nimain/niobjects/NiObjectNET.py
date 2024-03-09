import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiObjectNET(NiObject):

	"""
	Abstract base class for NiObjects that support names, extra data, and time controllers.
	"""

	__name__ = 'NiObjectNET'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Configures the main shader path
		self.shader_type = name_type_map['BSLightingShaderType'](self.context, 0, None)

		# Name of this controllable object, used to refer to the object in .kf files.
		self.name = name_type_map['String'](self.context, 0, None)
		self.legacy_extra_data = name_type_map['LegacyExtraData'](self.context, 0, None)

		# Extra data object index. (The first in a chain)
		self.extra_data = name_type_map['Ref'](self.context, 0, name_type_map['NiExtraData'])

		# The number of Extra Data objects referenced through the list.
		self.num_extra_data_list = name_type_map['Uint'](self.context, 0, None)

		# List of extra data indices.
		self.extra_data_list = Array(self.context, 0, name_type_map['NiExtraData'], (0,), name_type_map['Ref'])

		# Controller object index. (The first in a chain)
		self.controller = name_type_map['Ref'](self.context, 0, name_type_map['NiTimeController'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shader_type', name_type_map['BSLightingShaderType'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and (context.bs_header.bs_version >= 83) and (context.bs_header.bs_version <= 139), True)
		yield 'name', name_type_map['String'], (0, None), (False, None), (None, None)
		yield 'legacy_extra_data', name_type_map['LegacyExtraData'], (0, None), (False, None), (lambda context: context.version <= 33751040, None)
		yield 'extra_data', name_type_map['Ref'], (0, name_type_map['NiExtraData']), (False, None), (lambda context: 50331648 <= context.version <= 67240448, None)
		yield 'num_extra_data_list', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 167772416, None)
		yield 'extra_data_list', Array, (0, name_type_map['NiExtraData'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 167772416, None)
		yield 'controller', name_type_map['Ref'], (0, name_type_map['NiTimeController']), (False, None), (lambda context: context.version >= 50331648, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 335675399 <= instance.context.version <= 335675399 and (instance.context.bs_header.bs_version >= 83) and (instance.context.bs_header.bs_version <= 139) and isinstance(instance, name_type_map['BSLightingShaderProperty']):
			yield 'shader_type', name_type_map['BSLightingShaderType'], (0, None), (False, None)
		yield 'name', name_type_map['String'], (0, None), (False, None)
		if instance.context.version <= 33751040:
			yield 'legacy_extra_data', name_type_map['LegacyExtraData'], (0, None), (False, None)
		if 50331648 <= instance.context.version <= 67240448:
			yield 'extra_data', name_type_map['Ref'], (0, name_type_map['NiExtraData']), (False, None)
		if instance.context.version >= 167772416:
			yield 'num_extra_data_list', name_type_map['Uint'], (0, None), (False, None)
			yield 'extra_data_list', Array, (0, name_type_map['NiExtraData'], (instance.num_extra_data_list,), name_type_map['Ref']), (False, None)
		if instance.context.version >= 50331648:
			yield 'controller', name_type_map['Ref'], (0, name_type_map['NiTimeController']), (False, None)
	def add_extra_data(self, extrablock):
		"""Add block to extra data list and extra data chain. It is good practice
		to ensure that the extra data has empty next_extra_data field when adding it
		to avoid loops in the hierarchy."""
		# add to the list
		num_extra = self.num_extra_data_list
		self.num_extra_data_list = num_extra + 1
		self.extra_data_list.append(extrablock)
		# add to the chain
		if not self.extra_data:
			self.extra_data = extrablock
		else:
			lastextra = self.extra_data
			while lastextra.next_extra_data:
				lastextra = lastextra.next_extra_data
			lastextra.next_extra_data = extrablock

	def remove_extra_data(self, extrablock):
		"""Remove block from extra data list and extra data chain.

		>>> from pyffi.formats.nif import NifFormat
		>>> block = NifFormat.NiNode()
		>>> block.num_extra_data_list = 3
		>>> block.extra_data_list.update_size()
		>>> extrablock = NifFormat.NiStringExtraData()
		>>> block.extra_data_list[1] = extrablock
		>>> block.remove_extra_data(extrablock)
		>>> [extra for extra in block.extra_data_list]
		[None, None]
		"""
		# remove from list
		new_extra_list = []
		for extraother in self.extra_data_list:
			if not extraother is extrablock:
				new_extra_list.append(extraother)
		self.num_extra_data_list = len(new_extra_list)
		self.reset_field("extra_data_list")
		for i, extraother in enumerate(new_extra_list):
			self.extra_data_list[i] = extraother
		# remove from chain
		if self.extra_data is extrablock:
			self.extra_data = extrablock.next_extra_data
		lastextra = self.extra_data
		while lastextra:
			if lastextra.next_extra_data is extrablock:
				lastextra.next_extra_data = lastextra.next_extra_data.next_extra_data
			lastextra = lastextra.next_extra_data

	def get_extra_datas(self):
		"""Get a list of all extra data blocks."""
		xtras = [xtra for xtra in self.extra_data_list]
		xtra = self.extra_data
		while xtra:
			if not xtra in self.extra_data_list:
				xtras.append(xtra)
			xtra = xtra.next_extra_data
		return xtras

	def set_extra_datas(self, extralist):
		"""Set all extra data blocks from given list (erases existing data).

		>>> from pyffi.formats.nif import NifFormat
		>>> node = NifFormat.NiNode()
		>>> extra1 = NifFormat.NiExtraData()
		>>> extra1.name = "hello"
		>>> extra2 = NifFormat.NiExtraData()
		>>> extra2.name = "world"
		>>> node.get_extra_datas()
		[]
		>>> node.set_extra_datas([extra1, extra2])
		>>> [extra.name for extra in node.get_extra_datas()]
		[b'hello', b'world']
		>>> [extra.name for extra in node.extra_data_list]
		[b'hello', b'world']
		>>> node.extra_data is extra1
		True
		>>> extra1.next_extra_data is extra2
		True
		>>> extra2.next_extra_data is None
		True
		>>> node.set_extra_datas([])
		>>> node.get_extra_datas()
		[]
		>>> # now set them the other way around
		>>> node.set_extra_datas([extra2, extra1])
		>>> [extra.name for extra in node.get_extra_datas()]
		[b'world', b'hello']
		>>> [extra.name for extra in node.extra_data_list]
		[b'world', b'hello']
		>>> node.extra_data is extra2
		True
		>>> extra2.next_extra_data is extra1
		True
		>>> extra1.next_extra_data is None
		True

		:param extralist: List of extra data blocks to add.
		:type extralist: ``list`` of L{NifFormat.NiExtraData}
		"""
		# set up extra data list
		self.num_extra_data_list = len(extralist)
		self.reset_field("extra_data_list")
		for i, extra in enumerate(extralist):
			self.extra_data_list[i] = extra
		# set up extra data chain
		# first, kill the current chain
		self.extra_data = None
		# now reconstruct it
		if extralist:
			self.extra_data = extralist[0]
			lastextra = self.extra_data
			for extra in extralist[1:]:
				lastextra.next_extra_data = extra
				lastextra = extra
			lastextra.next_extra_data = None

	def add_controller(self, ctrlblock):
		"""Add block to controller chain and set target of controller to self."""
		if not self.controller:
			self.controller = ctrlblock
		else:
			lastctrl = self.controller
			while lastctrl.next_controller:
				lastctrl = lastctrl.next_controller
			lastctrl.next_controller = ctrlblock
		# set the target of the controller
		ctrlblock.target = self

	def get_controllers(self):
		"""Get a list of all controllers."""
		ctrls = []
		ctrl = self.controller
		while ctrl:
			ctrls.append(ctrl)
			ctrl = ctrl.next_controller
		return ctrls

	def add_integer_extra_data(self, name, value):
		"""Add a particular extra integer data block."""
		extra = NifFormat.classes.NiIntegerExtraData()
		extra.name = name
		extra.integer_data = value
		self.add_extra_data(extra)

