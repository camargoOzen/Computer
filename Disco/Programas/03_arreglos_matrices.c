// Arreglos y matrices con indices constantes

func void main() {
    int arr[3];
    int mat[2][2];

    arr[0] = 1;
    arr[1] = arr[0] + 2;

    mat[0][0] = arr[0];
    mat[0][1] = arr[1];
    mat[1][0] = 7;
    mat[1][1] = mat[0][1];
}
