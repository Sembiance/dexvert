from enum import EnumMeta, IntEnum, _EnumDict
import logging


class _AttributeEnumDict(_EnumDict):
	"""_non_members_ is added as special class variable much like _ignore_,
	except these are actually recorded on the class, rather than having to set
	them later
	"""

	def __init__(self):
		super().__init__()
		self._non_members_ = []

	def __setitem__(self, key, value):
		if key == "_non_members_":
			self._non_members_.append("_non_members_")
			# set _non_members_ on self to allow recovery for inheritance
			dict.__setitem__(self, key, value)
			self._non_members_ = value
		elif key in self._non_members_:
			dict.__setitem__(self, key, value)
		else:
			super().__setitem__(key, value)

# https://stackoverflow.com/questions/44867597/is-there-a-way-to-specify-a-default-value-for-python-enums
class DefaultEnumMeta(EnumMeta):
	default = object()

	@classmethod
	def __prepare__(metacls, cls, bases, **kwds):
		base_namespace = super().__prepare__(cls, bases, **kwds)
		# no easy way to convert between _EnumDict and _AttributeEnumDict, so
		# copy all vars and the content of the dictionary
		copied_namespace = _AttributeEnumDict()
		for key, item in vars(base_namespace).items():
			setattr(copied_namespace, key, item)
		copied_namespace.update(base_namespace)
		# Extend copied_namespace with _non_members_ of base classes, if they
		# have it. Will be overwritten by child _non_members_.
		for base in bases:
			if hasattr(base, "_non_members_"):
				copied_namespace._non_members_ = getattr(base, "_non_members_")
				break
		return copied_namespace

	def __call__(cls, *args, value=default, **kwargs):
		if value is DefaultEnumMeta.default:
			# Assume the first enum is default
			return next(iter(cls))
		return super().__call__(value, *args, **kwargs)

	# Execute base __new__ https://github.com/python/cpython/blob/32959108f9c543e3cb9f2b68bbc782bddded6f42/Lib/enum.py#L410
	# and then move __new__ to from_value, while the new __new__ accepts the standardized arguments
	def __new__(metacls, cls, bases, classdict, *args, **kwargs):
		# extract __name__ from the classdict and force it to be the class's name
		cls = classdict.get("__name__", cls)
		# extract all _non_members_ from the classdict
		stored_non_members_ = {}
		for key in classdict._non_members_:
			if key in classdict:
				stored_non_members_[key] = classdict.pop(key)
		# create the enum class with the modified data
		enum_class = super(metacls, metacls).__new__(metacls, cls, bases, classdict, *args, **kwargs)
		# reassign the extracted _non_members_ back to the class
		for key, value in stored_non_members_.items():
			setattr(enum_class, key, value)
		# move the __new__ function to from_value, and make the new __new__ behave like calling from_value without arguments
		new_function = enum_class.__new__
		# from_value doesn't need to be a proper __new__-like function, because specified enums can't be inherited from
		enum_class.from_value = classmethod(lambda cls, value: new_function(cls, value))
		enum_class.__new__ = lambda cls, context=None, arg=0, template=None, set_default=True: new_function(cls)
		return enum_class


class BaseEnum(IntEnum, metaclass=DefaultEnumMeta):

	def __int__(self):
		return self.value
	pass

	_non_members_ = ["_storage"]

	@classmethod
	def get_size(cls, instance, context, arg=0, template=None):
		return cls._storage.get_size(instance, context)

	@classmethod
	def from_stream(cls, stream, context=None, arg=0, template=None):
		value = cls._storage.from_stream(stream, None, 0, None)
		try:
			instance = cls.from_value(value)
		except ValueError:
			logging.debug(f"value {value} is not a member of the {cls} class, returning int")
			instance = value
		return instance

	@classmethod
	def to_stream(cls, instance, stream, context=None, arg=0, template=None):
		if isinstance(instance, cls):
			cls._storage.to_stream(instance.value, stream, context)
		else:
			logging.debug(f"instance {instance} is not a member of the {cls} class, writing int")
			cls._storage.to_stream(int(instance), stream, context)
		return instance

	def __str__(self):
		# maintain old behavior even for python 3.11
		cls_name = self.__class__.__name__
		return f'{cls_name}.{self.name}'

	@classmethod
	def from_str(cls, label):
		"""Creates the enum from its str representation"""
		assert "." in label
		value = label.split(".")[-1]
		try:
			enum = cls[value]
		except KeyError:
			raise KeyError(f"Key '{value}' not found in enum '{cls.__name__}', outdated definition?")
		return enum

	@staticmethod
	def fmt_member(member, indent=0):
		return str(member)

	@classmethod
	def from_xml(cls, target, elem, prop, arg=0, template=None):
		return cls.from_str(elem.attrib[prop])

	@classmethod
	def to_xml(cls, elem, prop, instance, arg, template, debug):
		elem.attrib[prop] = str(instance)

	@classmethod
	def validate_instance(cls, instance, context, arg, template):
		if not isinstance(instance, cls):
			logging.warning(f"instance {instance} is not a member of the {cls} class")
		cls._storage.validate_instance(int(instance))
