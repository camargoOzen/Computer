// Algoritmo de Euclides (restas sucesivas)

func void main() {
    int a = 48;
    int b = 18;

    while (a != b) {
        if (a > b) {
            a = a - b;
        } else {
            b = b - a;
        }
    }

    int gcd = a;
}
