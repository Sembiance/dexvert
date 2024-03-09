from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXSrc(NiObject):

	"""
	A source is a link between a Gamebryo object and a PhysX actor.
	"""

	__name__ = 'NiPhysXSrc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.active = name_type_map['Bool'].from_value(True)
		self.interpolate = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'active', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'interpolate', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'active', name_type_map['Bool'], (0, None), (False, True)
		yield 'interpolate', name_type_map['Bool'], (0, None), (False, None)
