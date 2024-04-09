
action drop() {
    x = 2w0;
}



control MyEgress(inout bit<2> y) {

    // action drop() {
    //     y = 2w2;
    // }

    apply {
        drop();
    }
}

bit<2> x;

MyEgress(x);