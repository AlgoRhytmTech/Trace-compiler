from enum import Enum, auto
from typing import List, Optional, Union

class TypeKind(Enum):
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    NULL = auto()
    VOID = auto()
    FUNCTION = auto()
    UNKNOWN = auto()  # For when we cannot determine the type

class Type:
    def __init__(self, kind: TypeKind,
                 param_types: Optional[List['Type']] = None,
                 return_type: Optional['Type'] = None):
        self.kind = kind
        self.param_types = param_types or []  # For FUNCTION
        self.return_type = return_type        # For FUNCTION

    def __eq__(self, other):
        return (self.kind == other.kind and
                self.param_types == other.param_types and
                self.return_type == other.return_type)

    def __repr__(self):
        if self.kind == TypeKind.FUNCTION:
            return f"Function({self.param_types} -> {self.return_type})"
        elif self.kind == TypeKind.UNKNOWN:
            return "Unknown"
        else:
            return self.kind.name

    def is_numeric(self):
        return self.kind in (TypeKind.INT, TypeKind.FLOAT)

    def is_comparable(self):
        return self.kind in (TypeKind.INT, TypeKind.FLOAT, TypeKind.STRING, TypeKind.BOOL)

    def is_logical(self):
        return self.kind == TypeKind.BOOL

# Predefined types
INT_TYPE = Type(TypeKind.INT)
FLOAT_TYPE = Type(TypeKind.FLOAT)
STRING_TYPE = Type(TypeKind.STRING)
BOOL_TYPE = Type(TypeKind.BOOL)
NULL_TYPE = Type(TypeKind.NULL)  
VOID_TYPE = Type(TypeKind.VOID)
UNKNOWN_TYPE = Type(TypeKind.UNKNOWN)