from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiCollisionObject(NiObject):

	"""
	This is the most common collision object found in NIF files. It acts as a real object that
	is visible and possibly (if the body allows for it) interactive. The node itself
	is simple, it only has three properties.
	For this type of collision object, bhkRigidBody or bhkRigidBodyT is generally used.
	"""

	__name__ = 'NiCollisionObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Index of the AV object referring to this collision object.
		self.target = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
