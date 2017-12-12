"""
    A base class of all types.
"""

import re
from abc import ABCMeta
from abc import abstractmethod

from clang import cindex

from regression_tests.parsers.c_parser import parse
from regression_tests.parsers.c_parser.utils import is_array_kind
from regression_tests.parsers.c_parser.utils import is_char_kind


class Type(metaclass=ABCMeta):
    """A base class of all types."""

    def __init__(self, type, complex_type_node=None):
        """
        :param clang.cindex.Type type: Internal type.
        :param clang.cindex.Cursor complex_type_node: node of complex type
         (enum, struct, union)
        """
        self._type = type

        if complex_type_node is not None:
            self._node = complex_type_node

    def is_void(self):
        """Is the type ``void``?"""
        return False

    def is_integral(self, size=None):
        """Is the type integral (``int``, ``long int``, etc.)?

        If `size` is not ``None``, it also checks if the type is of the given
        size (in bits).
        """
        return False

    def is_char(self, size=None):
        """Is the type ``char``?

        If `size` is not ``None``, it also checks if the type is of the given
        size (in bits).
        """
        return False

    def is_int(self, size=None):
        """Is the type ``int``?

        If `size` is not ``None``, it also checks if the type is of the given
        size (in bits).
        """
        return False

    def is_floating_point(self, size=None):
        """Is the type floating-point (``float``, ``double``, etc.)?

        If `size` is not ``None``, it also checks if the type is of the given
        size (in bits).
        """
        return False

    def is_float(self, size=None):
        """Is the type ``float``?

        If `size` is not ``None``, it also checks if the type is of the given
        size (in bits).
        """
        return False

    def is_double(self, size=None):
        """Is the type ``double``?

        If `size` is not ``None``, it also checks if the type is of the given
        size (in bits).
        """
        return False

    def is_pointer(self):
        """Is the type a pointer?"""
        return False

    def is_composite_type(self):
        """Is the type a composite type?"""
        return False

    def is_struct(self):
        """Is the type a structure?"""
        return False

    def is_union(self):
        """Is the type a union?"""
        return False

    def is_array(self):
        """Is the type an array?"""
        return False

    def is_enum(self):
        """Is the type an enum?"""
        return False

    def is_function(self):
        """Is the type a function?"""
        return False

    def is_bool(self):
        """Is the type a bool?"""
        return False

    def is_same_as(self, c_repr):
        """Is the type the same as the given type represented in C (`str`)?
        """
        return self == Type._from_c_repr(c_repr)

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self == other

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @staticmethod
    def _from_clang_type(type):
        """Creates a new type from the given clang type.

        :param clang.cindex.Type type: Internal type.

        :raises AssertionError: If the internal type is not supported.
        """
        # Basic types.
        if type.kind == cindex.TypeKind.VOID:
            return VoidType(type)
        elif is_char_kind(type):
            return CharType(type)
        elif type.kind in [cindex.TypeKind.INT, cindex.TypeKind.UINT]:
            return IntType(type)
        elif type.kind == cindex.TypeKind.FLOAT:
            return FloatType(type)
        elif type.kind in [cindex.TypeKind.DOUBLE, cindex.TypeKind.LONGDOUBLE]:
            return DoubleType(type)
        elif type.kind == cindex.TypeKind.POINTER:
            return PointerType(type)
        elif type.kind == cindex.TypeKind.BOOL:
            return BoolType(type)
        # If function pointer is a parameter of a function, it's type is not UNEXPOSED
        elif type.kind in [cindex.TypeKind.FUNCTIONPROTO,
                           cindex.TypeKind.FUNCTIONNOPROTO]:
            return FunctionType(type)
        elif is_array_kind(type):
            return ArrayType(type)

        # Unexposed or elaborated types. Elaborated types represent types that
        # were referred to using an elaborated type keyword, e.g. `struct S`
        # (http://clang.llvm.org/doxygen/classclang_1_1ElaboratedType.html).
        if type.kind in [cindex.TypeKind.UNEXPOSED, cindex.TypeKind.ELABORATED]:
            canonical_type = type.get_canonical()
            # Structure (a record in Clang terms).
            if canonical_type.kind == cindex.TypeKind.RECORD:
                if canonical_type.spelling.partition(' ')[0] == 'union':
                    return UnionType(canonical_type)
                else:
                    return StructType(canonical_type)
            # Function
            elif canonical_type.kind in [cindex.TypeKind.FUNCTIONPROTO,
                                         cindex.TypeKind.FUNCTIONNOPROTO]:
                return FunctionType(type)

        # Typedefs.
        if type.kind == cindex.TypeKind.TYPEDEF:
            # Standard typedefs.
            m = re.fullmatch(r'u?int(\d+)_t', type.spelling)
            if m is not None:
                return IntType(type, int(m.group(1)))

            # Our custom typedefs.
            m = re.fullmatch(r'float(\d+)_t', type.spelling)
            if m is not None:
                size = int(m.group(1))
                canonical_type = type.get_canonical()
                if canonical_type.kind == cindex.TypeKind.FLOAT:
                    return FloatType(type, size)
                elif canonical_type.kind == cindex.TypeKind.DOUBLE:
                    return DoubleType(type, size)

        raise AssertionError('unsupported type of kind {}'.format(type.kind))

    @staticmethod
    def _from_c_repr(c_repr):
        """Creates a type from the given C representation (`str`).

        For example, creates :class:`.IntType` from ``"int"``.
        """
        # We create a dummy module with a global variable of the requested type,
        # parse that module, and return the type of the global variable.
        # Include stdint.h to recognize the intX_t typedefs.
        module = parse("""
            #include <stdint.h>

            {} a;
        """.format(c_repr))
        return module.global_vars['a'].type


from regression_tests.parsers.c_parser.types.array_type import ArrayType
from regression_tests.parsers.c_parser.types.bool_type import BoolType
from regression_tests.parsers.c_parser.types.char_type import CharType
from regression_tests.parsers.c_parser.types.double_type import DoubleType
from regression_tests.parsers.c_parser.types.float_type import FloatType
from regression_tests.parsers.c_parser.types.function_type import FunctionType
from regression_tests.parsers.c_parser.types.int_type import IntType
from regression_tests.parsers.c_parser.types.pointer_type import PointerType
from regression_tests.parsers.c_parser.types.struct_type import StructType
from regression_tests.parsers.c_parser.types.union_type import UnionType
from regression_tests.parsers.c_parser.types.void_type import VoidType
