from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkAction import BhkAction
from nifgen.formats.nif.imports import name_type_map


class BhkUnaryAction(BhkAction):

	"""
	Bethesda extension of hkpUnaryAction. hkpUnaryAction performs an action on one body.
	"""

	__name__ = 'bhkUnaryAction'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.entity = name_type_map['Ptr'](self.context, 0, name_type_map['BhkRigidBody'])
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'entity', name_type_map['Ptr'], (0, name_type_map['BhkRigidBody']), (False, None), (None, None)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'entity', name_type_map['Ptr'], (0, name_type_map['BhkRigidBody']), (False, None)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
