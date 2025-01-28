#include <iostream>
using namespace std;

int main() {
    int b;
    int max = 73;
    cin >> b;
    if (max>b) {
        cout << "DODAJ" << endl;
    } else {
        cout << "IZVADI";
    }
    cout << abs(max-b);
}