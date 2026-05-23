INCLUDE "euclides"

DEFINE PI 3.1416

struct punto{
    int x;
    int y;
};

func int pow(int a, int b){
    int result = 1;

    for(int i = 0; i < b; i = i + 1){
        result = result *a;
    }
    return result;
}


func float area_circulo(float r){
    return PI * r*r;
}


func void main(){
    int x = 2;
    int y = 2;
    int resultado_pow;
    float resultado_area;
    float r = 2.0;
    int arr[3];
    int mat[2][2];
    struct punto p1;
    struct punto p2;
    bool p1_mayor;
    bool anidado;

    
    p1.x = 4;
    p1.y = 3;
    p2.x = 1;
    p2.y = 2;
    


    x = 22* 2 -3 *y;

    resultado_pow = pow(x, y);
    resultado_area = area_circulo(r);

    int i = 0;
    while(i < 3){
        arr[i] = i * 2;
        i = i + 1;
    }
    
    for(int i = 0; i < 2; i = i + 1){
        for(int j = 0; j < 2; j = j + 1){
            mat[i][j] = i + j;
        }
    }

    if(p1.x > p2.x && p1.y > p2.y){
        p1_mayor = true;
    } else {
        p1_mayor = false;
    }

    if(2 < 1){
        anidado = false;
    }else if(1 < 2){
        anidado = true;
    }else{
        anidado = false;
    }
}

