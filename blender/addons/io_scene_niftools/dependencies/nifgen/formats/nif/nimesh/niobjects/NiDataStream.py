from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiDataStream(NiObject):

	__name__ = 'NiDataStream'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.usage = name_type_map['DataStreamUsage'](self.context, 0, None)
		self.access = name_type_map['DataStreamAccess'](self.context, 0, None)

		# The size in bytes of this data stream.
		self.num_bytes = name_type_map['Uint'](self.context, 0, None)
		self.cloning_behavior = name_type_map['CloningBehavior'].CLONING_SHARE

		# Number of regions (such as submeshes).
		self.num_regions = name_type_map['Uint'](self.context, 0, None)

		# The regions in the mesh. Regions can be used to mark off submeshes which are independent draw calls.
		self.regions = Array(self.context, 0, None, (0,), name_type_map['Region'])

		# Number of components of the data (matches corresponding field in MeshData).
		self.num_components = name_type_map['Uint'](self.context, 0, None)

		# The format of each component in this data stream.
		self.component_formats = Array(self.context, 0, None, (0,), name_type_map['ComponentFormat'])
		self.data = name_type_map['DataStreamData'](self.context, (self.num_bytes, self.component_formats), None)
		self.streamable = name_type_map['Bool'].from_value(True)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'usage', name_type_map['DataStreamUsage'], (0, None), (False, None), (None, None)
		yield 'access', name_type_map['DataStreamAccess'], (0, None), (False, None), (None, None)
		yield 'num_bytes', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'cloning_behavior', name_type_map['CloningBehavior'], (0, None), (False, name_type_map['CloningBehavior'].CLONING_SHARE), (None, None)
		yield 'num_regions', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'regions', Array, (0, None, (None,), name_type_map['Region']), (False, None), (None, None)
		yield 'num_components', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'component_formats', Array, (0, None, (None,), name_type_map['ComponentFormat']), (False, None), (None, None)
		yield 'data', name_type_map['DataStreamData'], (None, None), (False, None), (None, None)
		yield 'streamable', name_type_map['Bool'], (0, None), (False, True), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if include_abstract:
			yield 'usage', name_type_map['DataStreamUsage'], (0, None), (False, None)
			yield 'access', name_type_map['DataStreamAccess'], (0, None), (False, None)
		yield 'num_bytes', name_type_map['Uint'], (0, None), (False, None)
		yield 'cloning_behavior', name_type_map['CloningBehavior'], (0, None), (False, name_type_map['CloningBehavior'].CLONING_SHARE)
		yield 'num_regions', name_type_map['Uint'], (0, None), (False, None)
		yield 'regions', Array, (0, None, (instance.num_regions,), name_type_map['Region']), (False, None)
		yield 'num_components', name_type_map['Uint'], (0, None), (False, None)
		yield 'component_formats', Array, (0, None, (instance.num_components,), name_type_map['ComponentFormat']), (False, None)
		yield 'data', name_type_map['DataStreamData'], ((instance.num_bytes, instance.component_formats), None), (False, None)
		yield 'streamable', name_type_map['Bool'], (0, None), (False, True)
