
struct metadata_t {
    bit<2> spec;
    bit<2> grp;
}



/////////////////////////////////////////////

control MyCtrl(inout bit<2> x,
               inout metadata_t metadata) 
{
    
    action drop(inout metadata_t metadata) {
        mark_to_drop(metadata);
    }

    action multicast(inout metadata_t metadata) {
        metadata.grp = 1;
    }

    action mac_forward(bit<2> m, bit<2> n, inout bit<2> x, inout metadata_t metadata) {
        metadata.spec = m;
        x = n
    }

    table mac_lookup {
        key = {
            hdr.ethernet.srcAddr : exact;
        }
        actions = {
            multicast(metadata);
            mac_forward(metadata);
            drop(metadata);
        }
        size = 1024;
        default_action = multicast(metadata);
    }
    apply {
            apply.mac_lookup [hdr.ethernet.srcAddr];
    }
}


bit<3> x;
metadata_t stm;

MyCtrl(x, stm);