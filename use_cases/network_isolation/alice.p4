/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x0800;
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


header alice {
    bit<8> value;
}

header bob {
    bit<8> value;
}

header telem_t {
    bit<8> value;
} 

struct headers {
    alice       alice_data;
    bob         bob_data;
    ethernet_t  ethernet;
    ipv4_t      ipv4;
    telem_t     telem;
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
        extract(Ipacket, hdr.alice_data);
        extract(Ipacket, hdr.bob_data);
        extract(Ipacket, hdr.ethernet);
        extract(Ipacket, hdr.ipv4);
        extract(Ipacket, hdr.telem);
        transition select() {
            default : accept;
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


control Alice_Ingress() {
    
    action set_by_alice(bit<8> val) {
        if (val == 8w1){
            hdr.alice_data.value = 8w1; // ALLOWED: Alice can update her fields
        }
        else {
            hdr.alice_data.value = 8w0; // ALLOWED: Alice can update her fields
        }

        //hdr.bob_data.value = val; // VIOLATION: Alice should no write to Bob's fields
        
        //hdr.telem.value = hdr.telem.value + 8w1; // ALLOWED: modify telemetry using telemetry information
        //hdr.alice_data.value = hdr.telem.value; // VIOLATION: leak telemetry information to Alice
    }

    table update_by_alice {
        key = {
            hdr.ethernet.dstAddr: exact;
        }
        actions = {
            set_by_alice;
        }
    }
    apply {
        apply.update_by_alice [hdr.ethernet.dstAddr];
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
        emit(Opacket, hdr.alice_data);
        emit(Opacket, hdr.bob_data);
        emit(Opacket, hdr.ethernet);
        emit(Opacket, hdr.ipv4);
        emit(Opacket, hdr.telem);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
Alice_Ingress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;