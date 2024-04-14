
struct metadata_t {
    bit<2> spec;
    bit<2> grp;
}



/////////////////////////////////////////////

control MyCtrl() 
{
    action drop() {
        mark_to_drop(metadata);
    }

    action multicast() {
        metadata.grp = 2w1;
    }

    action mac_forward(bit<2> port) {
        metadata.spec = port;
    }

    table mac_lookup {
        key = {
            srcAddr : exact;
        }
        actions = {
            multicast;
            mac_forward;
            drop;
        }
        size = 1024;
        default_action = multicast;
    }
    apply {
            apply.mac_lookup [srcAddr];
    }
}


bit<3> srcAddr;
metadata_t metadata;

MyCtrl();