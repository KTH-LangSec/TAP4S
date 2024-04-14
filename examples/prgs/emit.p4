
header headers {
    bit<3> dstAddr;
    bit<3> srcAddr;
}

/* PARSER */
parser MyParser(packet_in packet, inout headers hdr) {

    state start {
        extract(packet, hdr);
        hdr.dstAddr = 3w0;
    }
}

/* DEPARSER */
control MyDeparser(out packet_out packet, in headers hdr) {
    apply {
        emit(packet, hdr);
    }
}

headers hdr;
packet_in pin;
packet_out pout;

MyParser(pin, hdr);

MyDeparser(pout, hdr);