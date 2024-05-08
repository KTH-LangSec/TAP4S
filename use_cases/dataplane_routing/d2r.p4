/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x0800;
const bit<32> NUM_LINKS = 32w10;
const bit<32> THRESHOLD_1 = 32w10;
const bit<32> THRESHOLD_2 = 32w5;
// Priorities range between 0-7; 7 being the highest priority.
const bit<3> PRIO_1 = 3w7;
const bit<3> PRIO_2 = 3w4;
const bit<3> PRIO_3 = 3w2;
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header _bit_count {
    bit<32> bits_at_i;
}

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header _stack{
	bit<32> elem;
}

header BFS {
	bit<32> curr;
	bit<32> visited_vec_for_bfs;
	bit<32> path_taken;
	bit<32> next_node;
	bit<32> num_hops;
}

header broadcast_t {
    bit<32> id;
    bit<32> type;
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
    bit<1> version;
}

struct headers {
    BFS bfs;
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

bit<32> failures;

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
            default: accept;
        }
    }

    state ipv4 {
        extract(Ipacket, hdr.ipv4);
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

    /********************************************************/
    /***************** Modeled as an extern *****************/
    /********************************************************/
    // _bit_count[NUM_LINKS] bits_set_in;
    // _stack[10] stack1;
    // _stack[10] stack2;
    // bit stack_id = 0;
    // bit<32> path_taken = hdr.bfs.path_taken;
    // bit<32> failures =  bits_set_in[path_taken].bits_at_i - hdr.bfs.num_hops;
    // action push_neighbor(bit<32> n, bit<32> n_visited) {
    //     stack1.push_front(n);
    //     hdr.bfs.visited_vec_for_bfs = hdr.bfs.visited_vec_for_bfs| n_visited;
    // }

    // action pop_stack() {
	//    hdr.bfs.curr = stack1[0].elem;
    //    stack1.pop_front(1);
    // }

    // action change_stack() {
	//     stack_id = ~stack_id;
    //    	hdr.bfs.curr = stack1[0].elem;
	//     stack1.pop_front(1);
    // }

    
    // table bfs_step { 
    //     key={
	//         hdr.bfs.curr : exact;
	//         hdr.bfs.visited_vec_for_bfs : ternary;
	//         stack_id: exact;
    //     } 
    //     actions = {
    //         push_neighbor; pop_stack; change_stack;
    //     }
    // }

    action forwarding() {
        if (failures >= THRESHOLD_1) {
            hdr.ipv4.priority = PRIO_1;
        }
        else {
            if (failures >= THRESHOLD_2) {
                hdr.ipv4.priority = PRIO_2;
            }
            else {
                hdr.ipv4.priority = PRIO_3;
            }
        }
        // normal L2/L3 forwarding...
    }

    table forward {
	    key = {
	 	    hdr.bfs.next_node: exact;
	    }
	     actions = {
            forwarding;
            NoAction;
        }
	     default_action  = NoAction;
    }

     apply {
        // Calculate the failures number
        // Modeled as an extern
        calculate_failures(failures, hdr.bfs.num_hops);

        if(hdr.bfs.curr != hdr.ipv4.dstAddr) {
            bfs_step(); // Modeled as an extern
        }
        else {
            apply.forward [hdr.bfs.next_node];
        }
        
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