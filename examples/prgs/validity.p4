
header ipv4_t {
    bit<4>    version;
}

header myTunnel_t {
    bool    tun;
}

header ethernet_t {
    bit<2>    type;
}

struct headers {
    ethernet_t   ethernet;
    myTunnel_t   myTunnel;
    ipv4_t       ipv4;
}

headers hdr;

packet_in Ipacket;

extract(Ipacket, hdr.myTunnel);

bool val;
isValid(val, hdr.ethernet);