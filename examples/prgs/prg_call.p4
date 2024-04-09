bit<4> x;
bit<4> y;


bit<4> test_func (inout bit<4> a, in bit<4> b)
{
    b = 4w2;
    a = b + 4w4;
}

y = 4w0;

test_func(x, y);


