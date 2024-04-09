
header headers {
    bit<3> dstAddr;
    bit<3> srcAddr;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                out bit<3> y) {

    state start {
        transition select(true) {
            default: parse_ethernet;
        }
    }

    state parse_ethernet {
        extract(packet, hdr);
        transition select(hdr.dstAddr) {
            3w1: state_1;
            3w2: state_2;
            default: state_1;
        }
    }

    state state_1 {
        y = hdr.srcAddr;
    } 

    state state_2 {
        y = 3w2;
    } 
}

headers g_hdr;
packet_in p;
bit<3> x;

MyParser(p, g_hdr,x);