from enum import Enum

class TypesEnum(Enum):
    BIT_STRING = 1
    BOOL = 2
    STRUCT = 3
    HEADER = 3
    DEFINED = 3

class PrimitiveType():
    def __init__(self):
        pass

#################
class BitString(PrimitiveType):
    def __init__(self, _size):
        self.type = TypesEnum.BIT_STRING
        self.size = int(str(_size))

    def get_type(self):
        return self.type
    def get_size(self):
        return self.size

    def __str__(self):
        return "bit-string-"+ str(self.size)

#################
class Bool(PrimitiveType):
    def __init__(self):
        self.type = TypesEnum.BOOL

    def get_type(self):
        return self.type

    def __str__(self):
        return "boolean"

#######################################################
################# NON-PRIMITIVE TYPES #################
#######################################################
class Struct():
    def __init__(self):
        self.type = TypesEnum.STRUCT
        self.fields = []

    def add_field(self, _field):
        self.fields.append(_field)

    def get_type(self):
        return self.type
    def get_fields(self):
        return self.fields

    def __str__(self):
        ret = "< struct with FIELDS: "
        fields_lst = ', '.join(list(map(str, self.fields)))
        ret += "[ " + fields_lst + " ] >"
        return ret

#################
class Header():
    def __init__(self):
        self.type = TypesEnum.HEADER
        self.validity = True
        self.fields = []

    def set_validity(self, _val):
        self.validity = _val

    def get_validity(self):
        return self.validity

    def add_field(self, _field):
        self.fields.append(_field)

    def get_type(self):
        return self.type
    def get_fields(self):
        return self.fields

    def __str__(self):
        ret = "< header with FIELDS: "
        fields_lst = ', '.join(list(map(str, self.fields)))
        ret += "[ " + fields_lst + " ] >"
        return ret