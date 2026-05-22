INCLUDE "euclides"

DEFINE PI 3.1416
DEFINE E 2.7183

// Esta es una funcion para sumar dos numeros
func int sumar(int a, int b){
    return a + b;
}

func int pow(int a, int b){
    int result = 1;

    for(int i = 0; i < b; i = i + 1){
        result = result *a;
    }
    return result;
}

func float pow_float(float a, int b){
    float result = 1.0;

    for(int i = 0; i < b; i = i + 1){
        result = result *a;
    }
    return result;
}

func float area_circulo(float r){
    return PI * r*r;
}

func void main(){
    int x;
    int y = 2;
    int resultado_suma;
    int resultado_pow;
    float resultado_area;
    float r = 2.0;

    x = 22* 2 -3 *y;

    resultado_suma = sumar(x, y);
    resultado_pow = pow(x, y);
    resultado_area = pow_float(r, 2);
    resultado_area = area_circulo(r);

}

