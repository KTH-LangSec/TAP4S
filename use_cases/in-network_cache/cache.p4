/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bool MISS = false;
const bool HIT = true;
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


header _request {
    bit<8>   query;
}

header _response {
    bool status;
    bit<32>   value;
    bit<7> _padding;
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
    _request request;
    _response response;
    ethernet_t   ethernet;
    ipv4_t       ipv4;
}

/*****************************************************
**************** EXPLICIT DEFINITIONS ****************
******************************************************/
struct standard_metadata_t {
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
        extract(Ipacket, hdr.request);
        extract(Ipacket, hdr.response);

        extract(Ipacket, hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: ipv4;
            default: accept;
        }

    }

    state ipv4 {
        extract(Ipacket, hdr.ipv4);
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
    
    action get_repsonse(bit<32> value) {
        hdr.response.value = value;
        hdr.response.status = HIT;
    }
    
    action set_miss() {
        hdr.response.status = MISS;
    }

    table fetch_from_sever {
        key = {
            hdr.request.query: exact;
            hdr.response.status: exact;
        }
        actions = {
            get_repsonse;
        }
    }

    table fetch_from_cache {
        key = {
            hdr.request.query: exact;
        }
        actions = {
            get_repsonse;
            set_miss;
        }
        default_action = set_miss;
    }

    apply {
        // hdr.response.setValid();
        apply.fetch_from_cache [hdr.request.query];
        apply.fetch_from_sever [hdr.request.query, hdr.response.status];
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
        emit(Opacket, hdr.request);
        emit(Opacket, hdr.response);
        emit(Opacket, hdr.ethernet);
        emit(Opacket, hdr.ipv4);
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