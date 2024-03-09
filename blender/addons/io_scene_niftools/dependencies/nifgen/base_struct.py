import contextlib
import logging
import xml.etree.ElementTree as ET

import numpy as np

from nifgen.array import Array
from nifgen.context import ContextReference

# these attributes present on the MemStruct will not be stored on the XML
SKIPS = ("_context", "arg", "name", "io_start", "io_size", "template")
DTYPE = "dtype"
DO_NOT_SERIALIZE = "_"


class StructMetaClass(type):

    def __new__(metacls, name, bases, dict, **kwds):
        name = dict.get("__name__", name)
        return super().__new__(metacls, name, bases, dict, **kwds)


def indent(e, level=0):
    i = "\n" + level * "	"
    if len(e):
        if not e.text or not e.text.strip():
            e.text = i + "	"
        if not e.tail or not e.tail.strip():
            e.tail = i
        for e in e:
            indent(e, level + 1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not e.tail or not e.tail.strip()):
            e.tail = i


class DummyInstance:
    def __init__(self, context, arg=0, template=None):
        self.context = context
        self.arg = arg
        self.template = template


class struct_record(np.record):

    def __getattribute__(self, attr):
        value = np.record.__getattribute__(self, attr)
        if attr in ('setfield', 'getfield', 'dtype'):
            return value
        field_type = self.dtype.fields.get(attr, None)
        if field_type:
            return value.view(field_type[0])
        else:
            return value


class BaseStruct(metaclass=StructMetaClass):

    context = ContextReference()

    _attribute_list = ()
    allow_np = False

    def __init__(self, context, arg=0, template=None, set_default=True):
        self.name = ''
        self._context = context
        self.arg = arg
        self.template = template
        self.io_size = 0
        self.io_start = 0

    def set_defaults(self):
        for f_name, f_type, arguments, (optional, default) in type(self)._get_filtered_attribute_list(self):
            try:
                if default is None:
                    # continue with standard arguments
                    field_value = f_type(self.context, *arguments)
                else:
                    # use the from_value function
                    field_value = f_type.from_value(*arguments[2:4], default)
            except:
                raise ValueError(f"Failed setting default on {type(self).__name__}.{f_name}")
            setattr(self, f_name, field_value)

    @classmethod
    def get_fields_str(cls, instance, indent=0):
        s = ''
        for f_name, f_type, arguments, _ in cls._get_filtered_attribute_list(instance):
            s += f'\n	* {f_name} = {f_type.fmt_member(cls.get_field(instance, f_name), indent+1)}'
        return s

    @staticmethod
    def fmt_member(member, indent=0):
        lines = str(member).split("\n")
        lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
        return "\n".join(lines_new)

    def get_info_str(self, indent=0):
        return f'{self.__name__} [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

    def __repr__(self, indent=0):
        s = self.get_info_str(indent)
        s += self.get_fields_str(self, indent)
        s += '\n'
        return s

    @classmethod
    def from_xml_file(cls, file_path, context, arg=0, template=None):
        """Load Struct represented by the xml in 'file_path'"""
        instance = cls(context, arg, template, set_default=False)
        tree = ET.parse(file_path)
        xml = tree.getroot()
        try:
            cls._from_xml(instance, xml)
        except:
            logging.exception("from_xml_file failed")
        return instance

    @classmethod
    def from_xml(cls, target, elem, prop, arg, template):
        """Creates object for parent object 'target', from parent element elem."""
        sub = elem.find(f'./{prop}')
        if sub is None:
            logging.warning(f"Missing sub-element '{prop}' on XML element '{elem.tag}'")
            return
        instance = cls(target.context, arg, template, set_default=False)
        cls._from_xml(instance, sub)
        return instance

    @classmethod
    def _from_xml(cls, instance, elem):
        """Sets the data from the XML to this struct"""
        set_fields = set()
        # go over all (active through conditions) fields of this struct
        for f_name, f_type, arguments, (optional, default) in cls._get_filtered_attribute_list(instance):
            set_fields.add(f_name)
            # skip dummy properties
            if f_name in SKIPS:
                continue
            # keep clean XML
            if f_name.startswith(DO_NOT_SERIALIZE) or (optional and not elem.attrib.get(f_name)):
                continue
            setattr(instance, f_name, f_type.from_xml(instance, elem, f_name, *arguments))

        # also add any meta-data that is not directly part of the struct generated by the codegen
        for attr, value in elem.attrib.items():
            if attr not in set_fields:
                # logging.debug(f"Adding string metadata '{attr} = {value}' from XML element '{elem.tag}'")
                setattr(instance, attr, value)
        return instance

    @classmethod
    @contextlib.contextmanager
    def to_xml_file(cls, instance, file_path, debug=False):
        """Create an xml elem representing this MemStruct, recursively set its data, indent and save to 'file_path'"""
        xml = ET.Element(cls.__name__)
        cls._to_xml(instance, xml, debug)
        if hasattr(instance.context, "context_to_xml"):
            instance.context.context_to_xml(xml, "game", instance.context, 0, None, debug)
        yield xml
        indent(xml)
        with open(file_path, 'wb') as outfile:
            outfile.write(ET.tostring(xml))

    @classmethod
    def to_xml(cls, elem, prop, instance, arg, template, debug):
        """Adds this struct to 'elem', recursively"""
        # elem = ET.SubElement(elem, cls.__name__)
        sub = ET.SubElement(elem, prop)
        cls._to_xml(instance, sub, debug)

    @classmethod
    def _to_xml(cls, instance, elem, debug):
        # add any meta-data that is not directly part of the struct generated by the codegen
        for prop, val in vars(instance).items():
            if "name" in prop and isinstance(val, str) and val:
                # logging.debug(f"Adding string metadata '{prop} = {val}' to XML element '{elem.tag}'")
                elem.attrib[prop] = val

        # go over all fields of this struct
        for f_name, f_type, arguments, (optional, default) in cls._get_filtered_attribute_list(instance):
            if f_name in SKIPS:
                continue
            field_value = getattr(instance, f_name)
            # keep clean XML
            if f_name.startswith(DO_NOT_SERIALIZE) or (optional and field_value == default):
                if not debug:
                    continue
            # even valid fields may be set to None in some edge cases
            if field_value is not None:
                f_type.to_xml(elem, f_name, field_value, *arguments, debug)

    @classmethod
    def read_fields(cls, stream, instance):
        for f_name, f_type, arguments, _ in cls._get_filtered_attribute_list(instance, include_abstract=False):
            try:
                setattr(instance, f_name, f_type.from_stream(stream, instance.context, *arguments))
                # todo - remove this. instead, ensure that context is the root object so that any versions are set
                # copy version to context
                if "version" in f_name:
                    setattr(instance.context, f_name, getattr(instance, f_name))
            except:
                raise BufferError(f"Failed reading '{cls.__name__}.{f_name}' at {stream.tell()}")

    @classmethod
    def write_fields(cls, stream, instance):
        for f_name, f_type, arguments, _ in cls._get_filtered_attribute_list(instance, include_abstract=False):
            try:
                f_type.to_stream(getattr(instance, f_name), stream, instance.context, *arguments)
            except:
                raise BufferError(f"Failed writing '{cls.__name__}.{f_name}' at {stream.tell()}")

    def reset_field(self, target_f_name):
        for f_name, f_type, arguments, (optional, default) in type(self)._get_filtered_attribute_list(self):
            if f_name == target_f_name:
                if default is None:
                    field_value = f_type(self.context, *arguments)
                else:
                    field_value = f_type.from_value(*arguments[2:4], default)
                type(self).set_field(self, target_f_name, field_value)
                return field_value
        else:
            logging.warning(f"Field {target_f_name} was not evaluated to be on type {type(self).__name__}")

    @classmethod
    def validate_instance(cls, instance, context, arg, template):
        cls_name = cls.__name__
        try:
            if not callable(getattr(cls, 'from_value', None)):
                # if cls has from_value, the context on that type doesn't matter
                assert instance.context == context, f"context {instance.context} doesn't match {context} on {cls_name}"
            assert instance.arg == arg, f"argument {instance.argument} doesn't match {arg} on {cls_name}"
            assert instance.template == template, f"template {instance.template} doesn't match {template} on {cls_name}"
        except:
            raise ValueError(f"Validation failed on {cls_name}")
        for f_name, f_type, f_arguments, _ in cls._get_filtered_attribute_list(instance):
            try:
                f_type.validate_instance(cls.get_field(instance, f_name), context, *f_arguments)
            except:
                raise ValueError(f"Validation failed on {cls_name}.{f_name}")

    @classmethod
    def init_attributes(cls):

        def free_function(function_name):
            """Checks if the function is defined"""
            if function_name in cls.__dict__:
                return False
            else:
                # not defined in class body allows automatic filling, as long as any parents are also compatible
                return callable(getattr(cls, function_name, lambda: True))

        # if attribute list is not defined and we have the function to generate it, create it
        if "_attribute_list" not in cls.__dict__ and not free_function("_get_attribute_list"):
            cls._attribute_list = tuple(cls._get_attribute_list())

        # check if the class has a non-empty _attribute_list
        if getattr(cls, "_attribute_list", ()):
            attribute_list = cls._attribute_list
            # for convenience, sort the attribute list into continuous lists
            attr_names, attr_types, _, _, attr_conds = zip(*attribute_list)
            if all(all(cond is None for cond in cond_tuple) for cond_tuple in attr_conds) \
               and all(attr_type is not None for attr_type in attr_types):
                # all fields are static
                if len(set(attr_types)) == 1:
                    # every field is the same type, iteration makes sense
                    if free_function("__len__"):
                        cls.__len__ = lambda self: len(attribute_list)
                    if free_function("__iter__"):
                        def __iter__(self):
                            yield from (getattr(self, attr_name) for attr_name in attr_names)
                        cls.__iter__ = __iter__
                    if free_function("__getitem__"):
                        def __getitem__(self, key):
                            if 0 <= key < len(attribute_list):
                                return getattr(self, attr_names[key])
                            else:
                                raise IndexError(f'Index {key} not in {type(self)}')
                        cls.__getitem__ = __getitem__
                    if free_function("__setitem__"):
                        def __setitem__(self, key, value):
                            if 0 <= key < len(attribute_list):
                                return setattr(self, attr_names[key], value)
                            else:
                                raise IndexError(f'Index {key} not in {type(self)}')
                        cls.__setitem__ = __setitem__
                # check if all of the class's attributes have a from_value function
                if all(callable(getattr(attr_type, "from_value", None)) for attr_type in attr_types):
                    # since all fields are static and have a from_value function defined, this struct can also have
                    # from_value defined
                    if free_function("from_value"):
                        def from_value(value):
                            # from_value implies context-independence so pass None as context
                            instance = cls(None)
                            for f_name, f_type, value_element in zip(attr_names, attr_types, value):
                                setattr(instance, f_name, f_type.from_value(value_element))
                            return instance
                        cls.from_value = from_value
            # check if all of the class's attributes have a from_value function
            if getattr(cls, "allow_np", False) and all(
                    # check for a struct with get_np_dtype and flag set to True
                    callable(getattr(attr_type, "get_np_dtype", None)) or
                    # or a basic numeric type
                    getattr(attr_type, "np_dtype", None)
                    for attr_type in attr_types):
                if free_function("create_array"):
                    def create_array(shape, default=None, context=None, arg=0, template=None):
                        np_dtype = cls.get_np_dtype(context, arg, template)
                        return np.zeros(shape, dtype=np_dtype)
                    cls.create_array = create_array
                if free_function("read_array"):
                    def read_array(stream, shape, context=None, arg=0, template=None):
                        np_dtype = cls.get_np_dtype(context, arg, template)
                        array = np.empty(shape, dtype=np_dtype)
                        stream.readinto(array)
                        return array
                    cls.read_array = read_array
                if free_function("write_array"):
                    def write_array(instance, stream):
                        # todo - do type conversion, cf. basic.py
                        assert isinstance(instance, np.ndarray)
                        # np_dtype = cls.get_np_dtype(context, arg, template)
                        stream.write(instance.tobytes())
                    cls.write_array = write_array

    @classmethod
    def _get_attribute_list(cls):
        yield from ()

    @classmethod
    def _get_filtered_attribute_list(cls, instance, include_abstract=True):
        yield from ()

    @classmethod
    def get_conditioned_attributes(cls, struct_type, struct_instance, condition_function, arguments=(),
                                   include_abstract=True):
        for attribute in struct_type._get_filtered_attribute_list(struct_instance, *arguments[3:4], include_abstract):
            if condition_function(attribute):
                yield attribute

    @classmethod
    def get_condition_attributes_recursive(cls, struct_type, struct_instance, condition_function, arguments=(),
                                           include_abstract=True, enter_condition=lambda x: True):
        # check if this has a filtered attribute list
        if callable(getattr(struct_type, "_get_filtered_attribute_list", None)):
            for attribute in struct_type._get_filtered_attribute_list(
                    struct_instance,
                    *arguments[3:4],
                    include_abstract):
                f_name, f_type, field_arguments = attribute[0:3]
                if condition_function(attribute):
                    yield struct_type, struct_instance, attribute
                if enter_condition(attribute):
                    yield from cls.get_condition_attributes_recursive(
                        f_type,
                        struct_type.get_field(struct_instance, f_name),
                        condition_function,
                        field_arguments,
                        include_abstract)

    @classmethod
    def get_condition_values_recursive(cls, instance, condition_function, arguments=(), include_abstract=True,
                                       enter_condition=lambda x: True):
        for s_type, s_inst, (f_name, f_type, arguments, _) in cls.get_condition_attributes_recursive(
                type(instance),
                instance,
                condition_function,
                arguments,
                include_abstract,
                enter_condition):
            try:
                val = s_type.get_field(s_inst, f_name)
                yield val
            except (AttributeError, KeyError):
                logging.exception(f"Struct: Could not get {f_name} of {s_inst} of type {s_type}{'[' + str(s_inst.dtype) + ']' if issubclass(s_type, list) else ''}")
                raise

    @staticmethod
    def get_field(instance, key):
        return getattr(instance, key)

    @classmethod
    def set_field(cls, instance, key, value):
        return setattr(instance, key, value)

    @classmethod
    def get_size(cls, instance, context, arg=0, template=None):
        """arguments is optional because it is not required for _get_filtered_attribute_list"""
        size = 0
        for f_name, f_type, arguments, _ in cls._get_filtered_attribute_list(instance, include_abstract=False):
            size += f_type.get_size(cls.get_field(instance, f_name), context, *arguments)
        return size

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        instance = cls(context, arg, template, set_default=False)
        instance.io_start = stream.tell()
        cls.read_fields(stream, instance)
        instance.io_size = stream.tell() - instance.io_start
        return instance

    @classmethod
    def to_stream(cls, instance, stream, context, arg=0, template=None):
        try:
            instance.io_start = stream.tell()
            cls.write_fields(stream, instance)
            instance.io_size = stream.tell() - instance.io_start
            return instance
        except:
            logging.exception(f"{cls.__name__}.to_stream failed on {instance}")
            raise

    @classmethod
    def get_np_sig(cls, instance):
        res = []
        for f_name, f_type, arguments, _ in cls._get_filtered_attribute_list(instance, include_abstract=False):
            if f_type == Array:
                raise AttributeError(f"Can't cast structs containing arrays to numpy")
            if f_type is not None:
                # numeric basic types have np_dtype set on the class
                if hasattr(f_type, "np_dtype"):
                    res.append((f_name, f_type.np_dtype))
                # structs may be able to get a structured dtype
                else:
                    # instance is fake anyway so don't try to get a child struct
                    res.append((f_name, f_type.get_np_sig(instance)))
        # dynamically subclass to get np.record behavior
        # it does not work when dtype is not a subclass of struct_record
        record = type(f"{cls.__name__}Record", (cls, struct_record), {})
        return record, res

    @classmethod
    def get_np_dtype(cls, context, arg=0, template=None):
        # fake an instance to be able to get version-dependent fields
        fake_inst = DummyInstance(context, arg, template)
        np_sig = cls.get_np_sig(fake_inst)
        return np.dtype(np_sig)

