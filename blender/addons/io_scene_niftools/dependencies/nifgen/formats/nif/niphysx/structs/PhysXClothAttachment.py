from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class PhysXClothAttachment(BaseStruct):

	__name__ = 'PhysXClothAttachment'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.shape = name_type_map['Ref'](self.context, 0, name_type_map['NiPhysXShapeDesc'])
		self.num_vertices = name_type_map['Uint'](self.context, 0, None)
		self.flags = name_type_map['Uint'](self.context, 0, None)
		self.positions = Array(self.context, 0, None, (0,), name_type_map['PhysXClothAttachmentPosition'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shape', name_type_map['Ref'], (0, name_type_map['NiPhysXShapeDesc']), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'positions', Array, (0, None, (None,), name_type_map['PhysXClothAttachmentPosition']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shape', name_type_map['Ref'], (0, name_type_map['NiPhysXShapeDesc']), (False, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None)
		if instance.num_vertices == 0:
			yield 'flags', name_type_map['Uint'], (0, None), (False, None)
		if instance.num_vertices > 0:
			yield 'positions', Array, (0, None, (instance.num_vertices,), name_type_map['PhysXClothAttachmentPosition']), (False, None)
