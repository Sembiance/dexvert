from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class NiBillboardNode(NiNode):

	"""
	These nodes will always be rotated to face the camera creating a billboard effect for any attached objects.
	
	In pre-10.1.0.0 the Flags field is used for BillboardMode.
	Bit 0: hidden
	Bits 1-2: collision mode
	Bit 3: unknown (set in most official meshes)
	Bits 5-6: billboard mode
	
	Collision modes:
	00 NONE
	01 USE_TRIANGLES
	10 USE_OBBS
	11 CONTINUE
	
	Billboard modes:
	00 ALWAYS_FACE_CAMERA
	01 ROTATE_ABOUT_UP
	10 RIGID_FACE_CAMERA
	11 ALWAYS_FACE_CENTER
	"""

	__name__ = 'NiBillboardNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The way the billboard will react to the camera.
		self.billboard_mode = name_type_map['BillboardMode'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'billboard_mode', name_type_map['BillboardMode'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837696:
			yield 'billboard_mode', name_type_map['BillboardMode'], (0, None), (False, None)
