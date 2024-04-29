/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x0800;
const bit<32> NUM_LINKS = 32w10;
const bit<32> THRESHOLD_1 = 32w10;
const bit<32> THRESHOLD_2 = 32w5;
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header _app {
    bit<8>   appID;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<3>    priority;
    bit<5>    service;
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

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    _app app;
}

/*****************************************************
**************** EXPLICIT DEFINITIONS ****************
******************************************************/
struct standard_metadata_t {
    bit<9> egress_spec;
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
        extract(Ipacket, hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            TYPE_IPV4: ipv4;
            default: app;
        }

    }

    state ipv4 {
        extract(Ipacket, hdr.ipv4);
        transition select(){
            default: app;
        }
    }

    state app {
        extract(Ipacket, hdr.app);
        transition select(){
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

    action allocate_resources(bit<3> priority, bit<9> port) {
        hdr.ipv4.priority = priority;
        standard_metadata.egress_spec = port;
    }

    table application_resources {
	    key = {
            hdr.app.appID: exact;
	    }
	    actions = {
            allocate_resources;
        }
    }


    action allocate_resources_using_subnet(bit<3> priority, bit<9> port) {
        hdr.ipv4.priority = priority;
        standard_metadata.egress_spec = port;
    }

    action ipv4_forward(macAddr_t dstAddr) {
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 8w1;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    table ipv4_lpm_forward {
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
        apply.application_resources [hdr.app.appID];
        apply.ipv4_lpm_forward [hdr.ipv4.dstAddr];
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress() {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum() {
     apply {
    }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser() {
    apply{
        emit(Opacket, hdr.ethernet);
        emit(Opacket, hdr.ipv4);
        emit(Opacket, hdr.app);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;