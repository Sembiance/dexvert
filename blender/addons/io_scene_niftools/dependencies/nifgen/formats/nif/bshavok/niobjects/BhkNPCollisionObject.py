from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiCollisionObject import NiCollisionObject


class BhkNPCollisionObject(NiCollisionObject):

	"""
	Fallout 4 Collision Object
	"""

	__name__ = 'bhkNPCollisionObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Note: The CK Preview scenegraph reports these bits incorrectly.
		self.flags = name_type_map['BhkCOFlags'].from_value(128)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['BhkSystem'])
		self.body_id = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 128), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['BhkSystem']), (False, None), (None, None)
		yield 'body_id', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 128)
		yield 'data', name_type_map['Ref'], (0, name_type_map['BhkSystem']), (False, None)
		yield 'body_id', name_type_map['Uint'], (0, None), (False, None)
