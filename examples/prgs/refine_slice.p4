bit<8> x;
//bit<4> y;
bool z;

typedef bit<32> ip4Addr_t;

struct test {
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

test hdr;

if (hdr.dstAddr[7:0] == 8w10)
{
    z = true;
}
else
{
    z = false;
}