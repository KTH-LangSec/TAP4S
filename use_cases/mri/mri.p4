/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<8>  UDP_PROTOCOL = 0x11;
const bit<16> TYPE_IPV4 = 0x0800;
const bit<5>  IPV4_OPTION_MRI = 5w31;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> switchID_t;
typedef bit<19> qdepth_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header ipv4_option_t {
    bit<1> copyFlag;
    bit<2> optClass;
    bit<5> option;
    bit<8> optionLength;
}

header mri_t {
    bit<16>  count;
}

header switch_t {
    switchID_t  swid;
    qdepth_t    qdepth;
}

struct ingress_metadata_t {
    bit<16>  count;
}

struct parser_metadata_t {
    bit<16>  remaining;
}

struct metadata {
    ingress_metadata_t   ingress_metadata;
    parser_metadata_t   parser_metadata;
}

struct headers {
    ethernet_t          ethernet;
    ipv4_t              ipv4;
    ipv4_option_t       ipv4_option;
    mri_t               mri;
    switch_t            swtraces;
}

/*****************************************************
**************** EXPLICIT DEFINITIONS ****************
******************************************************/
struct standard_metadata_t {
    bit<9> egress_spec;
    bit<19> deq_qdepth;
}

packet_in Ipacket;
packet_out Opacket;

headers hdr;
metadata meta;
standard_metadata_t standard_metadata;

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser() {

    state start {
        transition select() {
            default: parse_ethernet;
        }
    }

    state parse_ethernet {
        extract(Ipacket, hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        extract(Ipacket, hdr.ipv4);
        //verify(hdr.ipv4.ihl >= 5, error.IPHeaderTooShort);
        transition select(hdr.ipv4.ihl) {
            4w5             : accept;
            default       : parse_ipv4_option;
        }
    }

    state parse_ipv4_option {
        extract(Ipacket, hdr.ipv4_option);
        transition select(hdr.ipv4_option.option) {
            IPV4_OPTION_MRI: parse_mri;
            default: accept;
        }
    }

    state parse_mri {
        extract(Ipacket, hdr.mri);
        meta.parser_metadata.remaining = hdr.mri.count;
        transition select(meta.parser_metadata.remaining) {
            16w0 : accept;
            default: parse_swtrace;
        }
    }

    state parse_swtrace {
        extract(Ipacket, hdr.swtraces);
        transition select() {
            default: accept;
        }
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum() {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress() {

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 8w1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        bool ipv4_validity;
        isValid(ipv4_validity, hdr.ipv4);

        if (ipv4_validity) {
            apply.ipv4_lpm [hdr.ipv4.dstAddr];
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress() {

    action add_swtrace(switchID_t swid) {
        hdr.mri.count = hdr.mri.count + 16w1;

        // hdr.swtraces.push_front(1);
        // hdr.swtraces[0].setValid();
        // hdr.swtraces[0].swid = swid;
        // hdr.swtraces[0].qdepth = (qdepth_t)standard_metadata.deq_qdepth;
        hdr.swtraces.swid = swid;
        hdr.swtraces.qdepth = standard_metadata.deq_qdepth;

        hdr.ipv4.ihl = hdr.ipv4.ihl + 4w2;
        hdr.ipv4_option.optionLength = hdr.ipv4_option.optionLength + 8w8;
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w8;
    }

    table swtrace {
        key = {}
        actions = {
            add_swtrace;
            NoAction;
        }
        default_action = NoAction();
    }

    apply {
        bool mri_validity;
        isValid(mri_validity, hdr.mri);

        if (mri_validity) {
            apply.swtrace [];
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum() {
     apply {
        update_checksum(
            ipv4_validity,
            hdr.ipv4.version,
            hdr.ipv4.ihl,
            hdr.ipv4.diffserv,
            hdr.ipv4.totalLen,
            hdr.ipv4.identification,
            hdr.ipv4.flags,
            hdr.ipv4.fragOffset,
            hdr.ipv4.ttl,
            hdr.ipv4.protocol,
            hdr.ipv4.srcAddr,
            hdr.ipv4.dstAddr,
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser() {
    apply {
        emit(Opacket, hdr.ethernet);
        emit(Opacket, hdr.ipv4);
        emit(Opacket, hdr.ipv4_option);
        emit(Opacket, hdr.mri);
        emit(Opacket, hdr.swtraces);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
