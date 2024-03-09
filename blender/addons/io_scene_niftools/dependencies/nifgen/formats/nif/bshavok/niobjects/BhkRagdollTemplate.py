from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BhkRagdollTemplate(NiExtraData):

	"""
	Found in Fallout 3, more ragdoll info?  (meshes\ragdollconstraint\*.rdt)
	"""

	__name__ = 'bhkRagdollTemplate'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_bones = name_type_map['Uint'](self.context, 0, None)
		self.bones = Array(self.context, 0, name_type_map['NiObject'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones', Array, (0, name_type_map['NiObject'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones', Array, (0, name_type_map['NiObject'], (instance.num_bones,), name_type_map['Ref']), (False, None)
