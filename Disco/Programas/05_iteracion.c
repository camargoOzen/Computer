// Iteracion con for y do-while

func void main() {
    int i = 0;
    int sum = 0;

    for (int j = 0; j < 5; j = j + 1) {
        sum = sum + j;
    }

    do {
        sum = sum + 1;
        i = i + 1;
    } while (i < 3);
}
