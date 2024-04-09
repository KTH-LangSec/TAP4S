
bit<3> x;
bit<3> y;

x = 3w1;

struct test {
    bit<3> m;
    bit<3> n;
}

bit<3> func(out bit<3> a, out bit<3> b)
{
    someExtern(b);
}

test hdr;
func(hdr.m, hdr.n);
