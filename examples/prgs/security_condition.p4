

header ipv4_t {
    bit<2>  port;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

ipv4_t hdr;
packet_in Ipacket;
packet_out Opacket;


parser MyParser() {

    state start {
        extract(Ipacket, hdr);
        transition select() {
            default : accept;
        }
    }
}

control MyCtrl() {
    apply { 
        if (hdr.srcAddr[7:0] == 8w10)
        {
            hdr.dstAddr[7:0] = 8w198;
            hdr.dstAddr[31:8] = 24w1;
            hdr.port = 2w1;
        }
        else
        {
            hdr.port = 2w0;
        }
     }
}

control MyDeparser() {
    apply {
        emit(Opacket, hdr);
    }
}


V1Switch(
MyParser(),
MyCtrl(),
MyDeparser()
) main;