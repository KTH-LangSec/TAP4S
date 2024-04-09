// bool x;
// bit<4> y;
// bool z;

struct hdr_t {
    bit<4> a;
    bit<4> b;
    bool t;
}

hdr_t hdr;

if (hdr.a == 4w4)
{
    hdr.t = true;
}
else
{
    hdr.t = false;
}