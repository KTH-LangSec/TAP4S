from enum import Enum
import type_system_lib.label as LATTICE
import type_system_lib.interval as INTERVAL

import logger as LOGGER


class TypesEnum(Enum):
    BIT_STRING = 1
    BOOL = 2
    STRUCT = 3
    HEADER = 4

    INPUT_PACKET = 100
    OUTPUT_PACKET = 101

##################
class PacketIn():
    def __init__(self):
        self.type = TypesEnum.INPUT_PACKET

    def get_type(self):
        return self.type

    def __str__(self):
        return "input packet bit-string"

##################
class PacketOut():
    def __init__(self):
        self.type = TypesEnum.OUTPUT_PACKET

    def get_type(self):
        return self.type

    def __str__(self):
        return "output packet bit-string"

##################
class Bool():
    def __init__(self, _value=None, _label=LATTICE.Low(), _interval=None):
        self.type = TypesEnum.BOOL
        self.label = _label

        if (_interval == None):
            if (_value != None):
                interval = INTERVAL.Interval(_value , _value, 1)
            else:
                interval = INTERVAL.Interval(0, 1, 1)
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

    def set_interval(self, _interval):
        self.interval = _interval

    def is_true(self):
        return self.interval.is_true()

    def is_false(self):
        return self.interval.is_false()

    def __str__(self):
        return "< bool, " + str(self.interval) + ", " + str(self.label) + " >"


##################
class BitString():
    def __init__(self, _size, _value=None, _label=LATTICE.Low(), _interval=None, _slices=None):
        self.type = TypesEnum.BIT_STRING
        self.size = _size
        self.slices = []
    
        if (_interval == None):
            if (_value != None):
                interval = INTERVAL.Interval(_value , _value, self.size)
            else:
                interval = INTERVAL.Interval(0, (2 ** self.size) - 1, self.size)
        else:
            interval = _interval
        
        if (_slices == None):
            slc = Slice(0, self.size-1, interval , _label)
            self.slices.append(slc)
        else:
            self.update_slices(_slices)

    def has_same_slices_as(self, _other_bs):
        if (len(self.slices) != _other_bs.number_of_slices()):
            return False
        else:
            for i, slc in enumerate(self.slices):
                j,k = slc.get_slice_indices()
                n,m = _other_bs.get_slice(i).get_slice_indices()
                if (j != n or k != m):
                    return False
        return True


    def update_slices(self, _slices):
        self.slices = []
        start = 0
        for slc in _slices:
            size = slc.get_size()
            end = start+size-1
            tmp_slc = Slice(start, end, slc.get_interval() , slc.get_label())
            start = start+size
            self.slices.append(tmp_slc)

        self.update_size()
    
    def update_size(self):
        new_size = 0
        for slc in self.slices:
            new_size += slc.get_size()
        self.size = new_size

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
    def get_slices(self):
        return self.slices
    
    def get_label(self):
        total_label = LATTICE.Low()
        for slc in self.slices:
            total_label = LATTICE.lup(total_label, slc.get_label())
        return total_label

    def get_overlapping_slices(self, _slice):
        start, end = _slice.get_slice_indices()
        overlaps= []
        for slc in self.slices:
            s_start, s_end = slc.get_slice_indices()
            if (s_end >= start) and (s_start <= end):
                overlaps.append(slc)

        return overlaps



    def consume_sub_string(self, _size, _bool=False):
        if (self.size < _size):
            LOGGER.error("cannot extract " + str(_size) + " bits from a " + str(self.size) + " bits bit-string!")

        return_sub_slices = []
        keep_sub_slices = []
        size = _size
        for slc in self.slices:
            if (size > 0):
                if (size >= slc.get_size()):
                    return_sub_slices.append(slc)
                    size -= slc.get_size()
                else:
                    ret_slc, keep_slc = slc.split(size)
                    size = 0
                    return_sub_slices.append(ret_slc)
                    keep_sub_slices.append(keep_slc)
            else:
                keep_sub_slices.append(slc)

        self.update_slices(keep_sub_slices)

        if (_bool == False):
            return BitString(_size, _slices=return_sub_slices)
        else:
            return Bool(_interval=return_sub_slices[0].get_interval(), _label=return_sub_slices[0].get_label())
                    
            

    def __str__(self):
        slices_lst = ', '.join(list(map(str, self.slices)))
        return "< bs[" + str(self.size) + "] , {" + slices_lst + "} >"


##################
class Struct():
    def __init__(self):
        self.type = TypesEnum.STRUCT
        self.fields = {}

    def get_type(self):
        return self.type

    def add_field(self, _name, _type):
        self.fields[_name] = _type
    def update_field(self, _name, _type):
        self.fields[_name] = _type
    def get_field(self, _name):
        return self.fields[_name]

    def get_fields(self):
        return self.fields.items()

    def get_keys(self):
        return self.fields.keys()

    def has_the_same_fields_as(self, _other_struct):
        if (set(self.fields.keys()) != set(_other_struct.get_keys())):
            return False
        else:
            res = True
            for name, fld in self.fields.items():
                other_fld = _other_struct.get_field(name)
                if (fld.get_type() != other_fld.get_type()):
                    return False
                else:
                    match fld.get_type():
                        case TypesEnum.BOOL:
                            res = res and True
                        case TypesEnum.BIT_STRING:
                            res = res and fld.has_same_slices_as(other_fld)
                        case TypesEnum.STRUCT:
                            res = res and fld.has_the_same_fields_as(other_fld)
                        case TypesEnum.HEADER:
                            res = res and fld.has_the_same_fields_as(other_fld)
        return res

    def get_size(self):
        size = 0
        for fld_type in self.fields.values():
            size += fld_type.get_size()
        return size

    def get_label(self):
        total_label = LATTICE.Low()
        for fld in self.fields.values():
            total_label = LATTICE.lup(total_label, fld.get_label())
        return total_label
    
    def raise_label(self, _label):
        for fld in self.fields.values():
            fld.raise_label(_label)


    def __str__(self):
        fields_lst = []
        for key, value in self.fields.items():
            fields_lst.append(str(key) + ":" + str(value))
        fields = '; '.join(list(map(str, fields_lst)))
        return " < [ " + fields + " ] >"


##################
class Header():
    def __init__(self):
        self.type = TypesEnum.HEADER
        self.fields = {}
        self.validity = False

    def get_type(self):
        return self.type

    def add_field(self, _name, _type):
        self.fields[_name] = _type
    def update_field(self, _name, _type):
        self.fields[_name] = _type
    def get_field(self, _name):
        return self.fields[_name]

    def get_fields(self):
        return self.fields.items()

    def get_size(self):
        size = 0
        for fld_type in self.fields.values():
            size += fld_type.get_size()
        return size

    def get_keys(self):
        return self.fields.keys()

    def has_the_same_fields_as(self, _other_header):
        if (set(self.fields.keys()) != set(_other_header.get_keys())):
            return False
        else:
            res = True
            for name, fld in self.fields.items():
                other_fld = _other_header.get_field(name)
                if (fld.get_type() != other_fld.get_type()):
                    return False
                else:
                    match fld.get_type():
                        case TypesEnum.BOOL:
                            res = res and True
                        case TypesEnum.BIT_STRING:
                            res = res and fld.has_same_slices_as(other_fld)
                        case TypesEnum.STRUCT:
                            res = res and fld.has_the_same_fields_as(other_fld)
                        case TypesEnum.HEADER:
                            res = res and fld.has_the_same_fields_as(other_fld)
        return res
    
    def set_validity(self):
        self.validity = True
    def get_validity(self):
        return self.validity

    def get_label(self):
        total_label = LATTICE.Low()
        for fld in self.fields.values():
            total_label = LATTICE.lup(total_label, fld.get_label())
        return total_label
    
    def raise_label(self, _label):
        for fld in self.fields.values():
            fld.raise_label(_label)

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

        self.size = int(self.end - self.start) + 1

    def raise_label(self, _label):
        self.label = LATTICE.lup(self.label, _label)

    def get_interval(self):
        return self.interval
    def get_label(self):
        return self.label
    def get_slice_indices(self):
        return (self.start, self.end)
    def get_size(self):
        return self.size

    def set_interval(self, _interval):
        self.interval = _interval

    def split(self, _split_index):
        length = self.size

        bin_min = int_to_binary(self.interval.get_min(), length)
        bin_max = int_to_binary(self.interval.get_max(), length)

        a, b = split_binary_at_index(bin_min, _split_index)
        c, d = split_binary_at_index(bin_max, _split_index)

        ## ret
        r_size = _split_index

        r_start = 0
        r_end = r_size - 1
        
        r_max_val = (2 ** r_size) - 1
        r_min = min(int(a, 2), int(c, 2)) 
        r_max = max(int(a, 2), int(c, 2))

        ret_slc = Slice(r_start, r_end, INTERVAL.Interval(r_min, r_max, r_size), self.label)
        
        # keep
        k_size = int(length - _split_index)

        k_start = 0
        k_end = k_size - 1

        r_max_val = (2 ** k_size) - 1
        
        if (int(b, 2) > int(d, 2)): # the interval is [max, min]
            k_min = 0
            k_max = r_max_val
        else:
            if xor_binary(a, c): # xor of first part was one, so there was a loop
                k_min = 0
                k_max = r_max_val
            else:
                k_min = min(int(b, 2), int(d, 2)) 
                k_max = max(int(b, 2), int(d, 2))

        keep_slc = Slice(k_start, k_end, INTERVAL.Interval(k_min, k_max, k_size), self.label)

        return(ret_slc, keep_slc)

    def __str__(self):
        return "( " + str(self.start) + " , " + str(self.end) + " ) -> ( " + str(self.interval) + " , " + str(self.label) + " )"


############################################################
################## SPLIT HELPER FUNCTIONS ##################
############################################################
def int_to_binary(_number, _length):
    binary = bin(_number)[2:]  # Convert to binary and remove the '0b' prefix
    padded_binary = binary.zfill(_length)  # Pad with zeros to match the desired length
    return padded_binary

def split_binary_at_index(binary_representation, index):
    if index < 0 or index >= len(binary_representation):
        raise ValueError("Index out of range")

    first_part = binary_representation[:index]
    second_part = binary_representation[index:]
    return first_part, second_part

def xor_binary(binary1, binary2):
    num1 = int(binary1, 2)
    num2 = int(binary2, 2)
    
    result = num1 ^ num2
    
    return result != 0