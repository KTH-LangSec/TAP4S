const bit<16> TYPE_MYTUNNEL = 0x1212;   // 4626
const bit<16> TYPE_IPV4 = 0x0800;       // 2048

header ethernet_t {
    bit<16>   etherType;
}

packet_in Ipacket;
ethernet_t hdr;
bit<2> x;

parser MyParser() {

    state start {
        transition select() {
            default : parse_ethernet;
        }
    }

    state parse_ethernet {
        extract(Ipacket, hdr);
        transition select(hdr.etherType) {
            TYPE_MYTUNNEL: parse_myTunnel;
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_myTunnel {
        x = 16w1;
        transition select() {
            default: accept;
        }
    }

    state parse_ipv4 {
        x = 16w2;
        transition select() {
            default : accept;
        }
    }

}

MyParser();