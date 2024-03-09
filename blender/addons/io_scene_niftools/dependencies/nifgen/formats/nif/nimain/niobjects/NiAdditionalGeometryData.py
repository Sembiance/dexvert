from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.AbstractAdditionalGeometryData import AbstractAdditionalGeometryData


class NiAdditionalGeometryData(AbstractAdditionalGeometryData):

	__name__ = 'NiAdditionalGeometryData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)
		self.num_block_infos = name_type_map['Uint'](self.context, 0, None)
		self.block_infos = Array(self.context, 0, None, (0,), name_type_map['NiAGDDataStream'])
		self.num_blocks = name_type_map['Uint'](self.context, 0, None)
		self.blocks = Array(self.context, 0, None, (0,), name_type_map['NiAGDDataBlocks'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_block_infos', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'block_infos', Array, (0, None, (None,), name_type_map['NiAGDDataStream']), (False, None), (None, None)
		yield 'num_blocks', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'blocks', Array, (0, None, (None,), name_type_map['NiAGDDataBlocks']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_block_infos', name_type_map['Uint'], (0, None), (False, None)
		yield 'block_infos', Array, (0, None, (instance.num_block_infos,), name_type_map['NiAGDDataStream']), (False, None)
		yield 'num_blocks', name_type_map['Uint'], (0, None), (False, None)
		yield 'blocks', Array, (0, None, (instance.num_blocks,), name_type_map['NiAGDDataBlocks']), (False, None)
