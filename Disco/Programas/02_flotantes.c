// Operaciones IEEE-754 con float

func void main() {
    float a = 3.5;
    float b = 2.0;
    float c = 0.0;

    c = a * b + 1.25;

    if (c > 0.0) {
        c = c / 2.0;
    } else {
        c = c + 0.5;
    }
}
