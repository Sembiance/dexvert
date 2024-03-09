from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class TextureType(BaseEnum):

	"""
	The type of information that is stored in a texture used by an NiTextureEffect.
	"""

	__name__ = 'TextureType'
	_storage = Uint


	# Apply a projected light texture. Each light effect is summed before multiplying by the base texture.
	TEX_PROJECTED_LIGHT = 0

	# Apply a projected shadow texture. Each shadow effect is multiplied by the base texture.
	TEX_PROJECTED_SHADOW = 1

	# Apply an environment map texture. Added to the base texture and light/shadow/decal maps.
	TEX_ENVIRONMENT_MAP = 2

	# Apply a fog map texture. Alpha channel is used to blend the color channel with the base texture.
	TEX_FOG_MAP = 3
