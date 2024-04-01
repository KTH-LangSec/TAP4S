from enum import Enum
import type_system_lib.label as LATTICE
import type_system_lib.interval as INTERVAL


class TypesEnum(Enum):
    BIT_STRING = 1
    BOOL = 2
    STRUCT = 3
    HEADER = 4

##################
class Bool():
    def __init__(self, _value=None, _label=LATTICE.Low(), _interval=None):
        self.type = TypesEnum.BOOL
        self.label = LATTICE.Low()

        if (_interval == None):
            if (_value != None):
                interval = INTERVAL.Interval(_value , _value)
            else:
                interval = INTERVAL.Interval(0, 1)
        else:
            interval = _interval

        self.interval = interval

    def raise_label(self, _label):
        self.label = LATTICE.lup(self.label, _label)

    def get_type(self):
        return self.type
    def get_size(self):
        return 1
    def get_interval(self):
        return self.interval
    def get_label(self):
        return self.label

    def __str__(self):
        return "< bool, " + str(self.interval) + ", " + str(self.label) + " >"


##################
class BitString():
    def __init__(self, _size, _value=None, _label=LATTICE.Low(), _interval=None, _slices=None):
        self.type = TypesEnum.BIT_STRING
        self.size = _size
    
        if (_interval == None):
            if (_value != None):
                interval = INTERVAL.Interval(_value , _value)
            else:
                interval = INTERVAL.Interval(0, (2 ** self.size) - 1)
        else:
            interval = _interval
        
        if (_slices == None):
            slc = Slice(0, self.size-1, interval , _label)
            self.slices = [slc]
        else:
            self.slices = _slices

    def raise_label(self, _label):
        for slc in self.slices:
            slc.raise_label(_label)

    def get_type(self):
        return self.type
    def get_size(self):
        return int(self.size)
    def number_of_slices(self):
        return len(self.slices)
    def get_slice(self, _number):
        if (_number < len(self.slices)):
            return self.slices[_number]

    def __str__(self):
        slices_lst = ', '.join(list(map(str, self.slices)))
        return "< bs[" + str(self.size) + "] , {" + slices_lst + "} >"


##################
class Struct():
    def __init__(self):
        self.type = TypesEnum.STRUCT
        self.fields = {}

    def add_field(self, _name, _type):
        self.fields[_name] = _type
    def update_field(self, _name, _type):
        self.fields[_name] = _type
    def get_field(self, _name):
        return self.fields[_name]

    def get_size(self):
        size = 0
        for fld_type in self.fields.values():
            size += fld_type.get_size()

    def __str__(self):
        fields_lst = []
        for key, value in self.fields.items():
            fields_lst.append(str(key) + ":" + str(value))
        fields = '; '.join(list(map(str, fields_lst)))
        return " < [ " + fields + " ] >"


##################
class Header():
    # TODO validity
    def __init__(self):
        self.type = TypesEnum.HEADER
        self.fields = {}

    def add_field(self, _name, _type):
        self.fields[_name] = _type
    def update_field(self, _name, _type):
        self.fields[_name] = _type
    def get_field(self, _name):
        return self.fields[_name]

    def __str__(self):
        fields_lst = []
        for key, value in self.fields.items():
            fields_lst.append(str(key) + ":" + str(value))
        fields = '; '.join(list(map(str, fields_lst)))
        return " < [ " + fields + " ] >"

##################################################
class Slice():
    def __init__(self, _start, _end, _interval, _label):
        self.start = _start
        self.end = _end
        self.label = _label
        self.interval = _interval

    def raise_label(self, _label):
        self.label = LATTICE.lup(self.label, _label)

    def get_interval(self):
        return self.interval
    def get_label(self):
        return self.label
    def get_slice_indices(self):
        return (self.start, self.end)

    def __str__(self):
        return "( " + str(self.start) + " , " + str(self.end) + " ) -> ( " + str(self.interval) + " , " + str(self.label) + " )"
