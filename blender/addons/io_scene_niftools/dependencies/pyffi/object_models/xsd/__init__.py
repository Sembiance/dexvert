"""This module provides a base class and a metaclass for parsing an XSD
schema and providing an interface for writing XML files that follow this
schema.
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
import time
import weakref
import xml.etree.cElementTree

import pyffi.object_models

class Tree(object):
    """Converts an xsd element tree into a tree of nodes that contain
    all information and methods for creating classes. Each node has a
    class matching the element type. The node constructor
    :meth:`Node.__init__` extracts the required information from the
    element and its children, thereby constructing the tree of nodes.
    Once the tree is constructed, call the :meth:`Node.class_walker`
    method to get a list of classes.
    """

    logger = logging.getLogger("pyffi.object_models.xsd")
    """For logging debug messages, warnings, and errors."""

    class Node(object):
        """Base class for all nodes in the tree."""

        schema = None
        """A weak proxy of the root element of the tree."""

        parent = None
        """A weak proxy of the parent element of this node, or None."""

        children = None
        """The child elements of this node."""

        logger = logging.getLogger("pyffi.object_models.xsd")
        """For logging debug messages, warnings, and errors."""

        def __init__(self, element, parent):
            # note: using weak references to avoid reference cycles
            self.parent = weakref.proxy(parent) if parent else None
            self.schema = self.parent.schema if parent else weakref.proxy(self)

            # create nodes for all children
            self.children = [Tree.node_factory(child, self)
                             for child in element.getchildren()]

        # note: this corresponds roughly to the 'clsFor' method in pyxsd
        def class_walker(self, fileformat):
            """Yields all classes defined under this node."""
            for child in self.children:
                for class_ in child.class_walker(fileformat):
                    yield class_

        def attribute_walker(self, fileformat):
            """Resolves all attributes."""
            for child in self.children:
                child.attribute_walker(fileformat)

        def instantiate(self, inst):
            """Create attributes on the instance *inst*."""
            for child in self.children:
                child.instantiate(inst)

        # helper functions
        @staticmethod
        def num_occurs(num):
            """Converts a string to an ``int`` or ``None`` (if unbounded)."""
            if num == 'unbounded':
                return None
            else:
                return int(num)

    class ClassNode(Node):
        """A node that corresponds to a class."""

        class_ = None
        """Generated class."""

    class All(Node):
        pass

    class Annotation(Node):
        pass

    class Any(Node):
        pass

    class AnyAttribute(Node):
        pass

    class Appinfo(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-attribute
    ##<attribute
    ##  default = string
    ##  fixed = string
    ##  form = (qualified | unqualified)
    ##  id = ID
    ##  name = NCName
    ##  ref = QName
    ##  type = QName
    ##  use = (optional | prohibited | required) : optional
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: (annotation?, simpleType?)
    ##</attribute>
    class Attribute(Node):
        """This class implements the attribute node, and also is a
        base class for the element node.
        """

        name = None
        """The name of the attribute."""

        ref = None
        """If the attribute is declared elsewhere, then this contains the name
        of the reference.
        """

        type_ = None
        """The type of the attribute. This determines the content this
        attribute can have.
        """

        pyname = None
        """Name for python."""

        pytype = None
        """Type for python."""

        def __init__(self, element, parent):
            Tree.Node.__init__(self, element, parent)
            self.name = element.get("name")
            self.ref = element.get("ref")
            self.type_ = element.get("type")
            if (not self.name) and (not self.ref):
                raise ValueError("Attribute %s has neither name nor ref."
                                 % element)

        def attribute_walker(self, fileformat):
            # attributes for child nodes
            Tree.Node.attribute_walker(self, fileformat)
            # now set attributes for this node
            if self.name:
                # could have self._type or not, but should not have a self.ref
                assert(not self.ref) # debug
                self.pyname = fileformat.name_attribute(self.name)
                node = self
            elif self.ref:
                # no name and no type should be defined
                assert(not self.name) # debug
                assert(not self.type_) # debug
                self.pyname = fileformat.name_attribute(self.ref)
                # resolve reference
                for child in self.schema.children:
                    if (isinstance(child, self.__class__)
                        and child.name == self.ref):
                        node = child
                        break
                else:
                    # exception for xml:base reference
                    if self.ref == "xml:base":
                        self.pytype = fileformat.XsString
                    else:
                        raise ValueError("Could not resolve reference to '%s'."
                                         % self.ref)
                    # done: name and type are resolved
                    return
            else:
                self.logger.error("Attribute without name.")
            if not node.type_:
                # resolve it locally
                for child in node.children:
                    # remember, ClassNode is simpletype or complextype
                    if isinstance(child, Tree.ClassNode):
                        self.pytype = child.class_
                        break
                else:
                    self.logger.warn(
                        "No type for %s '%s': falling back to xs:anyType."
                        % (self.__class__.__name__.lower(),
                           (self.name if self.name else self.ref)))
                    self.pytype = fileformat.XsAnyType
            else:
                # predefined type, or global type?
                pytypename = fileformat.name_class(node.type_)
                try:
                    self.pytype = getattr(fileformat, pytypename)
                except AttributeError:
                    raise ValueError(
                        "Could not resolve type '%s' (%s) for %s '%s'."
                        % (self.type_, pytypename,
                           self.__class__.__name__.lower(),
                           self.name if self.name else self.ref))

        def instantiate(self, inst):
            setattr(inst, self.pyname, self.pytype())

    class AttributeGroup(Node):
        pass

    class Choice(Node):
        pass

    class ComplexContent(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-complexType
    ##<complexType
    ##  abstract = boolean : false
    ##  block = (#all | List of (extension | restriction))
    ##  final = (#all | List of (extension | restriction))
    ##  id = ID
    ##  mixed = boolean : false
    ##  name = NCName
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: (annotation?, (simpleContent | complexContent | ((group | all | choice | sequence)?, ((attribute | attributeGroup)*, anyAttribute?))))
    ##</complexType>
    class ComplexType(ClassNode):
        name = None
        """The name of the type."""

        def __init__(self, element, parent):
            Tree.ClassNode.__init__(self, element, parent)
            self.name = element.get("name")

        def class_walker(self, fileformat):
            # construct a class name
            if self.name:
                class_name = self.name
            elif isinstance(self.parent, Tree.Element):
                # find element that contains this type
                class_name = self.parent.name
            else:
                raise ValueError(
                    "complexType has no name attribute and no element parent: "
                    "cannot determine name.")
            # filter class name so it conforms naming conventions
            class_name = fileformat.name_class(class_name)
            # construct bases
            class_bases = (Type,)
            # construct class dictionary
            class_dict = dict(_node=self, __module__=fileformat.__module__)
            # create class
            self.class_ = type(class_name, class_bases, class_dict)
            # assign child classes
            for child_class in Tree.Node.class_walker(self, fileformat):
                setattr(self.class_, child_class.__name__, child_class)
            # yield the generated class
            yield self.class_

    class Documentation(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-element
    ##<element
    ##  abstract = boolean : false
    ##  block = (#all | List of (extension | restriction | substitution))
    ##  default = string
    ##  final = (#all | List of (extension | restriction))
    ##  fixed = string
    ##  form = (qualified | unqualified)
    ##  id = ID
    ##  maxOccurs = (nonNegativeInteger | unbounded)  : 1
    ##  minOccurs = nonNegativeInteger : 1
    ##  name = NCName
    ##  nillable = boolean : false
    ##  ref = QName
    ##  substitutionGroup = QName
    ##  type = QName
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: (annotation?, ((simpleType | complexType)?, (unique | key | keyref)*))
    ##</element>
    # note: techically, an element is not quite an attribute, but for the
    #       purpose of this library, we can consider it as such
    class Element(Attribute):
        min_occurs = 1
        """Minimum number of times the element can occur. ``None``
        corresponds to unbounded.
        """

        max_occurs = 1
        """Maximum number of times the element can occur. ``None``
        corresponds to unbounded.
        """

        def __init__(self, element, parent):
            Tree.Attribute.__init__(self, element, parent)
            self.min_occurs = self.num_occurs(element.get("minOccurs",
                                                          self.min_occurs))
            self.max_occurs = self.num_occurs(element.get("maxOccurs",
                                                          self.max_occurs))

        def instantiate(self, inst):
            if self.min_occurs == 1 and self.max_occurs == 1:
                Tree.Attribute.instantiate(self, inst)
            else:
                # XXX todo
                pass

    class Enumeration(Node):
        pass

    class Extension(Node):
        pass

    class Field(Node):
        pass

    class Group(Node):
        pass

    class Import(Node):
        pass

    class Include(Node):
        pass

    class Key(Node):
        pass

    class Keyref(Node):
        pass

    class Length(Node):
        pass

    class List(Node):
        pass

    class MaxExclusive(Node):
        pass

    class MaxInclusive(Node):
        pass

    class MaxLength(Node):
        pass

    class MinInclusive(Node):
        pass

    class MinLength(Node):
        pass

    class Pattern(Node):
        pass

    class Redefine(Node):
        pass

    class Restriction(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-schema
    ##<schema
    ##  attributeFormDefault = (qualified | unqualified) : unqualified
    ##  blockDefault = (#all | List of (extension | restriction | substitution))  : ''
    ##  elementFormDefault = (qualified | unqualified) : unqualified
    ##  finalDefault = (#all | List of (extension | restriction | list | union))  : ''
    ##  id = ID
    ##  targetNamespace = anyURI
    ##  version = token
    ##  xml:lang = language
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: ((include | import | redefine | annotation)*, (((simpleType | complexType | group | attributeGroup) | element | attribute | notation), annotation*)*)
    ##</schema>
    class Schema(Node):
        """Class wrapper for schema tag."""

        version = None
        """Version attribute."""

        def __init__(self, element, parent):
            if parent is not None:
                raise ValueError("Schema can only occur as root element.")
            Tree.Node.__init__(self, element, parent)
            self.version = element.get("version")

    class Selector(Node):
        pass
        
    class Sequence(Node):
        pass

    class SimpleContent(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-simpleType
    ##<simpleType
    ##  final = (#all | List of (list | union | restriction))
    ##  id = ID
    ##  name = NCName
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: (annotation?, (restriction | list | union))
    ##</simpleType>
    class SimpleType(ClassNode):
        name = None
        """The name of the type."""

        def __init__(self, element, parent):
            Tree.ClassNode.__init__(self, element, parent)
            self.name = element.get("name")

        def class_walker(self, fileformat):
            # construct a class name
            if self.name:
                class_name = self.name
            elif isinstance(self.parent, Tree.Element):
                # find element that contains this type
                class_name = self.parent.name
            else:
                raise ValueError(
                    "simpleType has no name attribute and no element parent: "
                    "cannot determine name.")
            # filter class name so it conforms naming conventions
            class_name = fileformat.name_class(class_name)
            # construct bases
            class_bases = (Type,)
            # construct class dictionary
            class_dict = dict(_node=self)
            # create class
            self.class_ = type(class_name, class_bases, class_dict)
            # assign child classes
            for child_class in Tree.Node.class_walker(self, fileformat):
                setattr(self.class_, child_class.__name__, child_class)
            # yield the generated class
            yield self.class_

    class Union(Node):
        pass

    class Unique(Node):
        pass

    @classmethod
    # note: this corresponds to the 'factory' method in pyxsd
    def node_factory(cls, element, parent):
        """Create an appropriate instance for the given xsd element."""
        # get last part of the tag
        class_name = element.tag.split("}")[-1]
        class_name = class_name[0].upper() + class_name[1:]
        try:
            return getattr(cls, class_name)(element, parent)
        except AttributeError:
            cls.logger.warn("Unknown element type: making dummy node class %s."
                            % class_name)
            class_ = type(class_name, (cls.Node,), {})
            setattr(cls, class_name, class_)
            return class_(element, parent)

class MetaFileFormat(pyffi.object_models.MetaFileFormat):
    """The MetaFileFormat metaclass transforms the XSD description of a
    xml format into a bunch of classes which can be directly used to
    manipulate files in this format.

    The actual implementation of the parser is delegated to
    :class:`Tree`.
    """

    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare DaeFormat to have metaclass
        MetaFileFormat, so upon creation of the DaeFormat class,
        the __init__ function is called, with

        :param cls: The class created using MetaFileFormat, for example
            DaeFormat.
        :param name: The name of the class, for example 'DaeFormat'.
        :param bases: The base classes, usually (object,).
        :param dct: A dictionary of class attributes, such as 'xsdFileName'.
        """
        super(MetaFileFormat, cls).__init__(name, bases, dct)

        # open XSD file
        xsdfilename = dct.get('xsdFileName')
        if xsdfilename:
            # open XSD file
            xsdfile = cls.openfile(xsdfilename, cls.xsdFilePath, encoding="utf-8")

            # parse the XSD file
            cls.logger.debug("Parsing %s and generating classes." % xsdfilename)
            start = time.time()
            try:
                # create nodes for every element in the XSD tree
                schema = Tree.node_factory(
                    # XXX cElementTree python bug when running nosetests
                    #xml.etree.cElementTree.parse(xsdfile).getroot(), None)
                    xml.etree.ElementTree.parse(xsdfile).getroot(), None)
            finally:
                xsdfile.close()
            # generate classes
            for class_ in schema.class_walker(cls):
                setattr(cls, class_.__name__, class_)
            # generate attributes
            schema.attribute_walker(cls)
            cls.logger.debug("Parsing finished in %.3f seconds."
                             % (time.time() - start))

class Type(object):
    _node = None

    def __init__(self):
        if self._node is None:
            return
        # TODO initialize all attributes
        self._node.instantiate(self)

class FileFormat(pyffi.object_models.FileFormat, metaclass=MetaFileFormat):
    """This class can be used as a base class for file formats. It implements
    a number of useful functions such as walking over directory trees and a
    default attribute naming function.
    """
    xsdFileName = None #: Override.
    xsdFilePath = None #: Override.
    logger = logging.getLogger("pyffi.object_models.xsd")

    @classmethod
    def name_parts(cls, name):
        # introduces extra splits for some names
        name = name.replace("NMTOKEN", "NM_TOKEN") # name token
        name = name.replace("IDREF", "ID_REF") # identifier reference
        # do the split
        return pyffi.object_models.FileFormat.name_parts(name)

    # built-in datatypes
    # http://www.w3.org/TR/2004/REC-xmlschema-2-20041028/datatypes.html#built-in-datatypes

    class XsAnyType(object):
        """Abstract base type for all types."""
        pass

    class XsAnySimpleType(XsAnyType):
        """Abstract base type for all simple types."""
        pass

    class XsString(XsAnySimpleType):
        pass

    class XsBoolean(XsAnySimpleType):
        pass

    class XsDecimal(XsAnySimpleType):
        pass

    class XsFloat(XsAnySimpleType):
        pass

    class XsDouble(XsAnySimpleType):
        pass

    class XsDuration(XsAnySimpleType):
        pass

    class XsDateTime(XsAnySimpleType):
        pass

    class XsTime(XsAnySimpleType):
        pass

    class XsDate(XsAnySimpleType):
        pass

    class XsGYearMonth(XsAnySimpleType):
        pass

    class XsGYear(XsAnySimpleType):
        pass

    class XsGMonthDay(XsAnySimpleType):
        pass

    class XsGDay(XsAnySimpleType):
        pass

    class XsGMonth(XsAnySimpleType):
        pass

    class XsHexBinary(XsAnySimpleType):
        pass

    class XsBase64Binary(XsAnySimpleType):
        pass

    class XsAnyURI(XsAnySimpleType):
        pass

    class XsQName(XsAnySimpleType):
        pass

    class XsNotation(XsAnySimpleType):
        pass

    # derived datatypes
    # http://www.w3.org/TR/2004/REC-xmlschema-2-20041028/datatypes.html#built-in-derived

    class XsNormalizedString(XsString):
        pass

    class XsToken(XsNormalizedString):
        pass

    class XsLanguage(XsToken):
        pass

    class XsNmToken(XsToken):
        pass

    class XsNmTokens(XsToken):
        # list
        pass

    class XsName(XsToken):
        """Name represents XML Names. See
        http://www.w3.org/TR/2004/REC-xmlschema-2-20041028/datatypes.html#Name
        """
        pass

    class XsNCName(XsName):
        """NCName represents XML "non-colonized" Names. See
        http://www.w3.org/TR/2004/REC-xmlschema-2-20041028/datatypes.html#NCName
        """
        pass

    class XsId(XsNCName):
        pass

    class XsIdRef(XsNCName):
        pass

    class XsIdRefs(XsIdRef):
        # list
        pass

    class XsEntity(XsNCName):
        pass

    class XsEntities(XsEntity):
        # list
        pass

    class XsInteger(XsDecimal):
        pass

    class XsNonPositiveInteger(XsInteger):
        pass

    class XsNegativeInteger(XsInteger):
        pass

    class XsLong(XsInteger):
        pass

    class XsInt(XsLong):
        pass

    class XsShort(XsInt):
        pass

    class XsByte(XsShort):
        pass

    class XsNonNegativeInteger(XsInteger):
        pass

    class XsUnsignedLong(XsNonNegativeInteger):
        pass

    class XsUnsignedInt(XsUnsignedLong):
        pass

    class XsUnsignedShort(XsUnsignedInt):
        pass

    class XsUnsignedByte(XsUnsignedShort):
        pass

    class XsPositiveInteger(XsNonNegativeInteger):
        pass
