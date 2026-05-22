func int euclidespeña(int a, int b) {
    while (b > 0) {
        int c = a;
        a = b;
        b = c % b;
    }
    return a;
}