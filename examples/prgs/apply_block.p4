

header ethernet_t 
{
    /* empty */
}


struct metadata {
    /* empty */
}

// control MyVerifyChecksum(inout headers hdr) {
//     apply { 
        
//     }
// }

// control MyEgress(inout headers hdr,
//                  inout metadata meta,
//                  inout standard_metadata_t standard_metadata) {

//     action drop() {
//         mark_to_drop(standard_metadata);
//     }

//     apply {
//         if (standard_metadata.egress_port == standard_metadata.ingress_port)
//         {
//             drop();
//         }
//     }
// }