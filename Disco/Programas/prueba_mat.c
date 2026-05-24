func void main() {
    float mat1[2][3];
    float mat2[3][2];
    float result[2][2];

    mat1[0][0] = 1.0;
    mat1[0][1] = 2.0;
    mat1[0][2] = 3.0;
    mat1[1][0] = 4.0;
    mat1[1][1] = 5.0;
    mat1[1][2] = 6.0;

    mat2[0][0] = 1.0;
    mat2[0][1] = 1.0/2.0;
    mat2[1][0] = 1.0/3.0;
    mat2[1][1] = 1.0/4.0;
    mat2[2][0] = 1.0/5.0;
    mat2[2][1] = 1.0/6.0;

    for(int i = 0; i < 2; i = i+1) {
        for(int j = 0; j < 2; j = j+1) {
            result[i][j] = 0.0;
        }
    }

    for(int i = 0; i < 2; i = i+1) {

        for(int j = 0; j < 2; j = j+1) {

            for(int k = 0; k < 3; k = k+1) {

                result[i][j] = result[i][j] + mat1[i][k] * mat2[k][j];

            }
        }
    }

}