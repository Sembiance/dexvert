"""Format classes and metaclasses for binary file formats described by an xml
file, and xml handler for converting the xml description into Python classes.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import logging
import time # for timing stuff
import types
import os.path
import sys
import xml.etree.ElementTree as ET

import pyffi.object_models
from pyffi.object_models.xml.struct_    import StructBase
from pyffi.object_models.xml.basic      import BasicBase
from pyffi.object_models.xml.bit_struct import BitStructBase
from pyffi.object_models.xml.enum       import EnumBase
from pyffi.object_models.xml.expression import Expression


class MetaFileFormat(pyffi.object_models.MetaFileFormat):
    """The MetaFileFormat metaclass transforms the XML description
    of a file format into a bunch of classes which can be directly
    used to manipulate files in this format.

    The actual implementation of the parser is delegated to
    pyffi.object_models.xml.FileFormat.
    """

    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare NifFormat to have metaclass
        MetaFileFormat, so upon creation of the NifFormat class,
        the __init__ function is called, with

        :param cls: The class created using MetaFileFormat, for example
            NifFormat.
        :param name: The name of the class, for example 'NifFormat'.
        :param bases: The base classes, usually (object,).
        :param dct: A dictionary of class attributes, such as 'xml_file_name'.
        """

        super(MetaFileFormat, cls).__init__(name, bases, dct)

        # preparation: make deep copy of lists of enums, structs, etc.
        cls.xml_enum = cls.xml_enum[:]
        cls.xml_alias = cls.xml_alias[:]
        cls.xml_bit_struct = cls.xml_bit_struct[:]
        cls.xml_struct = cls.xml_struct[:]

        # parse XML

        # we check dct to avoid parsing the same file more than once in
        # the hierarchy
        xml_file_name = dct.get('xml_file_name')
        if xml_file_name:
            cls.logger.debug("Parsing %s and generating classes." % xml_file_name)
            # open XML file
            start = time.time()
            xml_file = cls.openfile(xml_file_name, cls.xml_file_path)
            xmlp = XmlParser(cls)
            try:
                xmlp.load_xml(xml_file)
            finally:
                xml_file.close()

            cls.logger.debug("Parsing finished in %.3f seconds." % (time.time() - start))

class FileFormat(pyffi.object_models.FileFormat, metaclass=MetaFileFormat):
    """This class can be used as a base class for file formats
    described by an xml file."""
    xml_file_name = None #: Override.
    xml_file_path = None #: Override.
    logger = logging.getLogger("pyffi.object_models.xml")

    # We also keep an ordered list of all classes that have been created.
    # The xml_struct list includes all xml generated struct classes,
    # including those that are replaced by a native class in cls (for
    # instance NifFormat.String). The idea is that these lists should
    # contain sufficient info from the xml so they can be used to write
    # other python scripts that would otherwise have to implement their own
    # xml parser. See makehsl.py for an example of usage.
    #
    # (note: no classes are created for basic types, so no list for those)
    xml_enum = []
    xml_alias = []
    xml_bit_struct = []
    xml_struct = []

class StructAttribute(object):
    """Helper class to collect attribute data of struct add tags."""

    def __init__(self, cls, attrs):
        """Initialize attribute from the xml attrs dictionary of an
        add tag.

        :param cls: The class where all types reside.
        :param attrs: The xml add tag attribute dictionary."""
        # mandatory parameters

        # The name of this member variable.
        self.displayname = attrs["name"]
        self.name = cls.name_attribute(self.displayname)
        # The type of this member variable (type is ``str`` for forward
        # declarations, and resolved to :class:`BasicBase` or :class:`StructBase` later).
        try:
            attrs_type_str = attrs["type"]
        except KeyError:
            raise AttributeError("'%s' is missing a type attribute" % self.displayname)
        if attrs_type_str != "TEMPLATE":
            try:
                self.type_ = getattr(cls, attrs_type_str)
            except AttributeError:
                # forward declaration, resolved in final_cleanup()
                self.type_ = attrs_type_str
        else:
            # type determined at runtime
            self.type_ = type(None)
        # optional parameters

        # default value of this member variable.
        self.default = attrs.get("default")
        # template type of this member variable (initially ``str``, resolved in final_cleanup() to :class:`BasicBase` or :class:`StructBase` at the end
        # of the xml parsing), and if there is no template type, then this variable will equal `None`.
        self.template = attrs.get("template")
        # argument of this member variable.
        self.arg = attrs.get("arg")
        # first array size of this member variable, as :class:`Expression` or `None`.
        self.arr1 = attrs.get("arr1")
        # second array size of this member variable, as :class:`Expression` or `None`.
        self.arr2 = attrs.get("arr2")
        # condition of this member variable, as :class:`Expression` or `None`.
        self.cond = attrs.get("cond")
        # version condition for this member variable
        self.vercond = attrs.get("vercond")
        # first version this member exists, as `int`, and `None` if there is no lower limit.
        self.ver1 = attrs.get("ver1")
        # last version this member exists, as `int`, and `None` if there is no upper limit.
        self.ver2 = attrs.get("ver2")
        # user version this member exists, as `int`, and `None` if it exists for all user versions.
        self.userver = attrs.get("userver")
        # docstring is handled in xml parser's characters function
        self.doc = ""
        # Whether the attribute is abstract or not (read and written).
        self.is_abstract = (attrs.get("abstract") in ("1", "true"))

        # post-processing
        if self.default:
            try:
                tmp = self.type_()
                tmp.set_value(self.default)
                self.default = tmp.get_value()
                del tmp
            except Exception:
                # conversion failed; not a big problem
                self.default = None
        if self.arr1:
            self.arr1 = Expression(self.arr1, cls.name_attribute)
        if self.arr2:
            self.arr2 = Expression(self.arr2, cls.name_attribute)
        if self.cond:
            self.cond = Expression(self.cond, cls.name_attribute)
        if self.vercond:
            self.vercond = Expression(self.vercond, cls.name_attribute)
        if self.arg:
            try:
                self.arg = int(self.arg)
            except ValueError:
                self.arg = cls.name_attribute(self.arg)
        if self.userver:
            self.userver = int(self.userver)
        if self.ver1:
            self.ver1 = cls.version_number(self.ver1)
        if self.ver2:
            self.ver2 = cls.version_number(self.ver2)

class BitStructAttribute(object):
    """Helper class to collect attribute data of bitstruct bits tags."""

    def __init__(self, cls, attrs):
        """Initialize attribute from the xml attrs dictionary of an
        add tag.

        :param cls: The class where all types reside.
        :param attrs: The xml add tag attribute dictionary."""
        # mandatory parameters
        self.name = cls.name_attribute(attrs["name"])
        self.numbits = int(cls.name_attribute(attrs["numbits"]))
        # optional parameters
        self.default = attrs.get("default")
        self.cond = attrs.get("cond")
        self.ver1 = attrs.get("ver1")
        self.ver2 = attrs.get("ver2")
        self.userver = attrs.get("userver")
        self.doc = "" # handled in xml parser's characters function

        # post-processing
        if self.default:
            self.default = int(self.default)
        if self.cond:
            self.cond = Expression(self.cond, cls.name_attribute)
        if self.userver:
            self.userver = int(self.userver)
        if self.ver1:
            self.ver1 = cls.version_number(self.ver1)
        if self.ver2:
            self.ver2 = cls.version_number(self.ver2)

class XmlError(Exception):
    """The XML handler will throw this exception if something goes wrong while
    parsing."""
    pass

class XmlParser:
    struct_types = ("compound", "niobject", "struct")
    bitstruct_types = ("bitfield", "bitflags", "bitstruct")
    def __init__(self, cls):
        """Set up the xml parser."""

        # initialize dictionaries
        # map each supported version string to a version number
        cls.versions = {}
        # map each supported game to a list of header version numbers
        cls.games = {}
        # note: block versions are stored in the _games attribute of the struct class

        # cls needs to be accessed in member functions, so make it an instance member variable
        self.cls = cls

        # elements for creating new classes
        self.class_name = None
        self.class_dict = None
        self.base_class = ()

        # elements for versions
        self.version_string = None

        # list of tuples ({tokens}, (target_attribs)) for each <token>
        self.tokens = [ ]
        self.versions = [ ([], ("versions", "until", "since")), ]

    def load_xml(self, file):
        """Loads an XML (can be filepath or open file) and does all parsing"""
        tree = ET.parse(file)
        root = tree.getroot()
        self.load_root(root)
        self.final_cleanup()
            
    def load_root(self, root):
        """Goes over all children of the root node and calls the appropriate function depending on type of the child"""
        for child in root:
            if child.tag in self.struct_types:
                res = self.read_struct(child)
            elif child.tag in self.bitstruct_types:
                res = self.read_bitstruct(child)
            elif child.tag == "basic":
                res = self.read_basic(child)
            elif child.tag == "alias":
                res = self.read_alias(child)
            elif child.tag == "enum":
                res = self.read_enum(child)
            elif child.tag == "module":
                res = self.read_module(child)
            elif child.tag == "version":
                res = self.read_version(child)
            elif child.tag == "token":
                res = self.read_token(child)

    # the following constructs do not create classes
    def read_token(self, token):
        """Reads an xml <token> block and stores it in the tokens list"""
        self.tokens.append( ([], token.attrib["attrs"].split(" ") ) )
        for sub_token in token:
            self.tokens[-1][0].append( (sub_token.attrib["token"], sub_token.attrib["string"]) )
        
    def read_version(self, version):
        """Reads an xml <version> block and stores it in the versions list"""
        # todo [versions] this ignores the user vers!
        # versions must be in reverse order so don't append but insert at beginning
        if "id" in version.attrib:
            self.versions[0][0].insert( 0, (version.attrib["id"], version.attrib["num"]) )
        # add to supported versions
        self.version_string = version.attrib["num"]
        self.cls.versions[self.version_string] = self.cls.version_number(self.version_string)
        self.update_gamesdict(self.cls.games, version.text)
        self.version_string = None
    
    def read_module(self, module):
        """Reads a xml <module> block"""
        # no children, not interesting for now
        pass

    def read_basic(self, basic):
        """Maps to a type defined in self.cls"""
        self.class_name = basic.attrib["name"]
        # Each basic type corresponds to a type defined in C{self.cls}.
        # The link between basic types and C{self.cls} types is done via the name of the class.
        basic_class = getattr(self.cls, self.class_name)
        # check the class variables
        is_template = self.is_generic(basic.attrib)
        if basic_class._is_template != is_template:
            raise XmlError( 'class %s should have _is_template = %s' % (self.class_name, is_template))

        # link class cls.<class_name> to basic_class
        setattr(self.cls, self.class_name, basic_class)
    
    # the following constructs create classes
    def read_bitstruct(self, bitstruct):
        """Create a bitstruct class"""
        attrs = self.replace_tokens(bitstruct.attrib)
        self.base_class = BitStructBase
        self.update_class_dict(attrs, bitstruct.text)
        try:
            numbytes = int(attrs["numbytes"])
        except KeyError:
            # niftools style: storage attribute
            numbytes = getattr(self.cls, attrs["storage"]).get_size()
        self.class_dict["_attrs"] = []
        self.class_dict["_numbytes"] = numbytes
        for member in bitstruct:
            attrs = self.replace_tokens(member.attrib)
            if member.tag == "bits":
                # eg. <bits name="Has Folder Records" numbits="1" default="1" />
                # mandatory parameters
                bit_attrs = attrs
            elif member.tag == "option":
                # niftools compatibility, we have a bitflags field
                # so convert value into numbits
                # first, calculate current bit position
                bitpos = sum(bitattr.numbits for bitattr in self.class_dict["_attrs"])
                # avoid crash
                if "value" in attrs:
                    # check if extra bits must be inserted
                    numextrabits = int(attrs["value"]) - bitpos
                    if numextrabits < 0:
                        raise XmlError("values of bitflags must be increasing")
                    if numextrabits > 0:
                        reserved = dict(name="Reserved Bits %i"% len(self.class_dict["_attrs"]), numbits=numextrabits)
                        self.class_dict["_attrs"].append( BitStructAttribute( self.cls, reserved))
                # add the actual attribute
                bit_attrs = dict(name=attrs["name"], numbits=1)
            # new nif xml    
            elif member.tag == "member":
                bit_attrs = dict(name=attrs["name"], numbits=attrs["width"])
            else:
                raise XmlError("only bits tags allowed in struct type declaration")
            
            self.class_dict["_attrs"].append( BitStructAttribute(self.cls, bit_attrs) )
            self.update_doc(self.class_dict["_attrs"][-1].doc, member.text)

        self.create_class(bitstruct.tag)

    def read_struct(self, struct):
        """Create a struct class"""
        attrs = self.replace_tokens(struct.attrib)
        self.update_class_dict(attrs, struct.text)
        # struct types can be organized in a hierarchy
        # if inherit attribute is defined, look for corresponding base block
        class_basename = attrs.get("inherit")
        if class_basename:
            # class_basename must have been assigned to a class
            try:
                self.base_class = getattr(self.cls, class_basename)
            except KeyError:
                raise XmlError( "typo, or forward declaration of struct %s" % class_basename)
        else:
            self.base_class = StructBase
        # set attributes (see class StructBase)
        # 'generic' attribute is optional- if not set, then the struct is not a template
        self.class_dict["_is_template" ] = self.is_generic(attrs)
        self.class_dict["_attrs" ] = []
        self.class_dict["_games" ] = {}
        for field in struct:
            attrs = self.replace_tokens(field.attrib)
            # the common case
            if field.tag in ("add", "field"):
                # add attribute to class dictionary
                self.class_dict["_attrs"].append( StructAttribute(self.cls, attrs) )
                self.update_doc(self.class_dict["_attrs"][-1].doc, field.text)
            # not found in current nifxml
            elif field.tag == "version":
                # set the version string
                self.version_string = attrs["num"]
                self.cls.versions[self.version_string] = self.cls.version_number(self.version_string)
                self.update_gamesdict(self.class_dict["_games"], field.text)
            else:
                print("only add and version tags allowed in struct declaration")
            # load defaults for this <field>
            for default in field:
                if default.tag != "default":
                    raise AttributeError("struct children's children must be 'default' tag")
        self.create_class(struct.tag)

    def read_enum(self, enum):
        """Create an enum class"""
        attrs = self.replace_tokens(enum.attrib)
        self.base_class = EnumBase
        self.update_class_dict(attrs, enum.text)
        try:
            numbytes = int(attrs["numbytes"])
        except KeyError:
            # niftools format uses a storage
            # get number of bytes from that
            typename = attrs["storage"]
            try:
                typ = getattr(self.cls, typename)
            except AttributeError:
                raise XmlError("typo, or forward declaration of type %s" % typename)
            numbytes = typ.get_size()
        # add stuff to classdict
        self.class_dict["_numbytes"] = numbytes
        self.class_dict["_enumkeys"] = []
        self.class_dict["_enumvalues"] = []
        for option in enum:
            attrs = self.replace_tokens(option.attrib)
            if option.tag not in ("option",):
                raise XmlError("only option tags allowed in enum declaration")
            value = attrs["value"]
            try:
                # note: use long rather than int to work around 0xffffffff
                # error in qskope
                value = int(value)
            except ValueError:
                value = int(value, 16)
            self.class_dict["_enumkeys"].append(attrs["name"])
            self.class_dict["_enumvalues"].append(value)
        self.create_class(enum.tag)

    def read_alias(self, alias):
        """Create an alias class, ie. one that gives access to another class"""
        self.update_class_dict(alias.attrib, alias.text)
        typename = alias.attrib["type"]
        try:
            self.base_class = getattr(self.cls, typename)
        except AttributeError:
            raise XmlError("typo, or forward declaration of type %s" % typename)
        self.create_class(alias.tag)


    # the following are helper functions
    def is_generic(self, attr):
        # be backward compatible
        return (attr.get("generic") == "true") or (attr.get("istemplate") == "1")

    def update_gamesdict(self, gamesdict, ver_text):
        if ver_text:
            # update the gamesdict dictionary
            for gamestr in (g.strip() for g in ver_text.split(',')):
                if gamestr in gamesdict:
                    gamesdict[gamestr].append(self.cls.versions[self.version_string])
                else:
                    gamesdict[gamestr] = [self.cls.versions[self.version_string]]
        
    def update_class_dict(self, attrs, doc_text):
        """This initializes class_dict, sets the class name and doc text"""
        doc_text = doc_text.strip() if doc_text else ""
        self.class_name = attrs["name"]
        self.class_dict = {"__doc__": doc_text, "__module__": self.cls.__module__}

    def update_doc(self, doc, doc_text):
        if doc_text:
            doc += doc_text.strip()
        
    def create_class(self, tag):
        """Creates a class for <tag> (tag name of the class that was just finished)"""
        # assign it to cls.<class_name> if it has not been implemented internally

        # type(name, bases, dict) returns a new type object, essentially a dynamic form of the class statement
        cls_klass = getattr(self.cls, self.class_name, None)
        # does the class exist?
        if cls_klass:
            # do nothing if this is a Basic type
            if issubclass(cls_klass, BasicBase):
                return
            # it has been created in format's __init__.py
            # create and add to base class of customizer
            gen_klass = type("_"+self.class_name, (self.base_class,), self.class_dict)
            setattr(self.cls, "_"+self.class_name, gen_klass)
            # recreate the class, to ensure that the metaclass is called!!
            # (otherwise, cls_klass does not have correct _attribute_list, etc.)
            cls_klass = type(cls_klass.__name__, (gen_klass,) + cls_klass.__bases__, dict(cls_klass.__dict__))
            setattr(self.cls, self.class_name, cls_klass)
            # if the class derives from Data, then make an alias
            if issubclass(cls_klass, pyffi.object_models.FileFormat.Data):
                self.cls.Data = cls_klass
            # for the stuff below
            gen_klass = cls_klass
        else:
            # does not yet exist: create it and assign to class dict
            gen_klass = type(self.class_name, (self.base_class,), self.class_dict)
            setattr(self.cls, self.class_name, gen_klass)
        # append class to the appropriate list
        if tag in self.struct_types:
            self.cls.xml_struct.append(gen_klass)
        elif tag in self.bitstruct_types:
            self.cls.xml_bit_struct.append(gen_klass)
        elif tag == "enum":
            self.cls.xml_enum.append(gen_klass)
        elif tag == "alias":
            self.cls.xml_alias.append(gen_klass)
            
    def replace_tokens(self, attr_dict):
        """Update attr_dict with content of tokens+versions list."""
        # replace versions after tokens because tokens include versions
        for tokens, target_attribs in self.tokens + self.versions:
            for target_attrib in target_attribs:
                if target_attrib in attr_dict:
                    expr_str = attr_dict[target_attrib]
                    for op_token, op_str in tokens:
                        expr_str = expr_str.replace(op_token, op_str)
                    attr_dict[target_attrib] = expr_str
        # additional tokens that are not specified by nif.xml
        fixed_tokens = ( ("\\", "."), ("&gt;", ">"), ("&lt;", "<"), ("&amp;", "&"), ("#ARG#", "ARG"), ("#T#", "TEMPLATE") )
        for attrib, expr_str in attr_dict.items():
            for op_token, op_str in fixed_tokens:
                expr_str = expr_str.replace(op_token, op_str)
            attr_dict[attrib] = expr_str
        # onlyT & excludeT act as aliases for deprecated cond
        prefs = ( ("onlyT", ""), ("excludeT", "!") )
        for t, pref in prefs:
            if t in attr_dict:
                attr_dict["cond"] = pref+attr_dict[t]
                break
        return attr_dict
        
    def final_cleanup(self):
        """Called when the xml is completely parsed.
        Searches and adds class customized functions.
        Fixes forward declaration of templates.
        """
        # get 'name_attribute' for all classes
        # we need this to fix them in cond="..." later
        klass_filter = {}
        for klass in self.cls.xml_struct:
            klass_filter[self.cls.name_attribute(klass.__name__)] = klass
        for obj in list(self.cls.__dict__.values()):
            # skip objects that are not generated by the C{type} function
            # or that do not derive from StructBase
            if not (isinstance(obj, type) and issubclass(obj, StructBase)):
                continue
            # fix templates
            for attr in obj._attrs:
                templ = attr.template
                if isinstance(templ, str):
                    attr.template =  getattr(self.cls, templ) if templ != "TEMPLATE" else type(None)
                attrtype = attr.type_
                if isinstance(attrtype, str):
                    attr.type_ = getattr(self.cls, attrtype)
                # fix refs to types in conditions
                if attr.cond:
                    attr.cond.map_(lambda x: klass_filter[x] if x in klass_filter else x)
