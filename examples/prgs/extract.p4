
// header headers {
//     bit<3> dstAddr;
//     bit<3> srcAddr;
// }

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(out bit<3> y) {

    state start {
        transition select(true) {
            default: parse_ethernet;
        }
    }

    state parse_ethernet {
        //extract(packet, hdr);
        transition select(addr) {
            4w1: state_1;
            4w4: state_2;
            4w15: state_2;
            default: state_3;
        }
    }

    state state_1 {
        y = 3w1;
    } 

    state state_2 {
        y = 3w2;
    }

    state state_3 {
        y = 3w3;
    } 
}

// headers hdr;
// packet_in packet;
bit<3> x;
bit<4> addr;

MyParser(x);