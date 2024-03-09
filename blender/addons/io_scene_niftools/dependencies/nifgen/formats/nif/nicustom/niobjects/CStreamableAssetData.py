from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class CStreamableAssetData(NiObject):

	"""
	Divinity 2 specific block
	"""

	__name__ = 'CStreamableAssetData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.root = name_type_map['Ref'](self.context, 0, name_type_map['NiNode'])
		self.has_data = name_type_map['Bool'](self.context, 0, None)
		self.data = name_type_map['ByteArray'](self.context, 0, None)
		self.num_refs = name_type_map['Uint'](self.context, 0, None)
		self.refs = Array(self.context, 0, name_type_map['NiObject'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'root', name_type_map['Ref'], (0, name_type_map['NiNode']), (False, None), (None, None)
		yield 'has_data', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['ByteArray'], (0, None), (False, None), (None, True)
		yield 'num_refs', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'refs', Array, (0, name_type_map['NiObject'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'root', name_type_map['Ref'], (0, name_type_map['NiNode']), (False, None)
		yield 'has_data', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_data:
			yield 'data', name_type_map['ByteArray'], (0, None), (False, None)
		yield 'num_refs', name_type_map['Uint'], (0, None), (False, None)
		yield 'refs', Array, (0, name_type_map['NiObject'], (instance.num_refs,), name_type_map['Ref']), (False, None)
