// // Include P4 core library
// # include <core.p4>

// // Include very simple switch architecture declarations
// # include "very_simple_switch_model.p4"

// This program processes packets comprising an Ethernet and an IPv4
// header, and it forwards packets using the destination IP address

typedef bit<48>  EthernetAddress;
typedef bit<32>  IPv4Address;

const bit<16> TYPE_IPV4 = 800;

// Standard Ethernet header
// header Ethernet_h {
//     EthernetAddress dstAddr;
//     EthernetAddress srcAddr;
//     bit<16>         etherType;
// }

// IPv4 header (without options)
header IPv4_h {
    bit<4>       version;
    bit<4>       ihl;
    bit<8>       diffserv;
    bit<16>      totalLen;
    bit<16>      identification;
    bit<3>       flags;
    bit<13>      fragOffset;
    bit<8>       ttl;
    bit<8>       protocol;
    bit<16>      hdrChecksum;
    IPv4Address  srcAddr;
    IPv4Address  dstAddr;
}

// // Structure of parsed headers
// struct Parsed_packet {
//     Ethernet_h ethernet;
//     IPv4_h     ip;
// }

struct test_str {
    bit<12> ethernet;
    IPv4Address     ip;
}


IPv4_h tst;
IPv4Address var;
var = tst.srcAddr;


// Match-action pipeline section
// 1. If OutControl is = 2, then packet is low, 
//    else packet is high once emitted.
// 2. A packet is secret when the dstAddr 
//or source address of the input packet is 10.0.0.0
control TopPipe(inout Parsed_packet headers,
                in error parseError, // parser error
                in InControl inCtrl, // input port
                out OutControl outCtrl) {
     IPv4Address nextHop;  // local variable

     /**
      * Indicates that a packet is dropped by setting the
      * output port to the DROP_PORT
      */
      action Drop_action() {
          outCtrl.outputPort = DROP_PORT;
      }

     /**
      * Set the next hop and the output port.
      * Decrements ipv4 ttl field.
      * @param ipv4_dest ipv4 address of next hop
      * @param port output port
      */
      action Set_nhop(IPv4Address ipv4_dest, PortId port) {
          nextHop = ipv4_dest;
          headers.ip.ttl = headers.ip.ttl - 1;
          outCtrl.outputPort = port;
      }

     /**
      * Computes address of next IPv4 hop and output port
      * based on the IPv4 destination of the current packet.
      * Decrements packet IPv4 TTL.
      * @param nextHop IPv4 address of next hop
      */
     table ipv4_match {
         key = { headers.ip.dstAddr: lpm; }  // longest-prefix match
         actions = {
              Drop_action;
              Set_nhop;
         }
         size = 1024;
         default_action = Drop_action;
     }


      apply ipv4_match [] ;
}

// deparser section
control TopDeparser(inout Parsed_packet p, packet_out o) {
    bit<1> validity;
    bit<16> ck;
    emit(o, p.ethernet);
    isValid(validity, p.ip);
    if (validity == 1) 
    {
        clear(ck);              // prepare checksum unit
        p.ip.hdrChecksum = 16; // clear checksum
        update(ck, p.ip);         // compute new checksum.
        bit<16> res;
        get(ch, res);
        p.ip.hdrChecksum = res;
    }
    emit(o, p.ip);
}



// Instantiate the top-level VSS package
VSS(TopParser(),
    TopPipe(),
    TopDeparser()) main;