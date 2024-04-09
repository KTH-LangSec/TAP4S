bool x;
bool z;
bit<4> y;

if (x == true)
{
    if (z == true)
    {
        y = 4w1;
    }
    else
    {
        y = 4w2;
    }
}
else
{
    y = 4w0;
}