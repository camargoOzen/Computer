// TDA: struct con acceso a campos

struct Punto {
    int x;
    int y;
};

func void main() {
    Punto p;
    p.x = 10;
    p.y = p.x + 5;
}
