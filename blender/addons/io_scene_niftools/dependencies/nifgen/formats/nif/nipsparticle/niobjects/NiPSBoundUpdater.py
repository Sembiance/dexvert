from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSBoundUpdater(NiObject):

	"""
	Updates the bounding volume for an NiPSParticleSystem object.
	"""

	__name__ = 'NiPSBoundUpdater'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of particle bounds to skip updating every frame. Higher = more updates each frame.
		self.update_skip = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'update_skip', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'update_skip', name_type_map['Ushort'], (0, None), (False, None)
