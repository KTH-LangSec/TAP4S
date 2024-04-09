struct test {
    bool val;
    bit<2> y;
}

header hdr_type {
    bit<5> val1;
    bit<5> type1;
}

packet_in packet;
test x;

hdr_type hdr;

extract(packet, hdr);

