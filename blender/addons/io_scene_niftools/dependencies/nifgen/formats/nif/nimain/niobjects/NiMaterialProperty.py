from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiMaterialProperty(NiProperty):

	"""
	Describes the surface properties of an object e.g. translucency, ambient color, diffuse color, emissive color, and specular color.
	"""

	__name__ = 'NiMaterialProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Property flags.
		self.flags = name_type_map['Ushort'](self.context, 0, None)

		# How much the material reflects ambient light.
		self.ambient_color = name_type_map['Color3'].from_value((1.0, 1.0, 1.0))

		# How much the material reflects diffuse light.
		self.diffuse_color = name_type_map['Color3'].from_value((1.0, 1.0, 1.0))

		# How much light the material reflects in a specular manner.
		self.specular_color = name_type_map['Color3'].from_value((1.0, 1.0, 1.0))

		# How much light the material emits.
		self.emissive_color = name_type_map['Color3'].from_value((0.0, 0.0, 0.0))

		# The material glossiness.
		self.glossiness = name_type_map['Float'].from_value(10.0)

		# The material transparency (1=non-transparant). Refer to a NiAlphaProperty object in this material's parent NiTriShape object, when alpha is not 1.
		self.alpha = name_type_map['Float'].from_value(1.0)
		self.emissive_mult = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: 50331648 <= context.version <= 167772418, None)
		yield 'ambient_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0)), (lambda context: context.bs_header.bs_version < 26, None)
		yield 'diffuse_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0)), (lambda context: context.bs_header.bs_version < 26, None)
		yield 'specular_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0)), (None, None)
		yield 'emissive_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0)), (None, None)
		yield 'glossiness', name_type_map['Float'], (0, None), (False, 10.0), (None, None)
		yield 'alpha', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'emissive_mult', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version > 21, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 50331648 <= instance.context.version <= 167772418:
			yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.bs_header.bs_version < 26:
			yield 'ambient_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0))
			yield 'diffuse_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0))
		yield 'specular_color', name_type_map['Color3'], (0, None), (False, (1.0, 1.0, 1.0))
		yield 'emissive_color', name_type_map['Color3'], (0, None), (False, (0.0, 0.0, 0.0))
		yield 'glossiness', name_type_map['Float'], (0, None), (False, 10.0)
		yield 'alpha', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.bs_header.bs_version > 21:
			yield 'emissive_mult', name_type_map['Float'], (0, None), (False, 1.0)
	def is_interchangeable(self, other):
		"""Are the two material blocks interchangeable?"""
		specialnames = (b"envmap2", b"envmap", b"skin", b"hair",
						b"dynalpha", b"hidesecret", b"lava")
		if self.__class__ is not other.__class__:
			return False
		if (self.name.lower() in specialnames
			or other.name.lower() in specialnames):
			# do not ignore name
			return self.get_hash() == other.get_hash()
		else:
			# ignore name
			return self.get_hash()[1:] == other.get_hash()[1:]
