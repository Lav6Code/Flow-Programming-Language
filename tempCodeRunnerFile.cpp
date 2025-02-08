#include <iostream>
#include <list>
#include <string>
using namespace std;


int index(const string& el, const list<string>& lst) {
    auto it = lst.begin();
    int i = 0;
    for(; it != lst.end(); ++it, ++i) {
        if(el==*it) {
            return i;
        }
    }
    return -1;
}
string getname(const string& el) {
    if(el=="V") {
        return "VEDRAN";
    } else if(el=="S"){
        return "STJEPAN";
    } else if(el=="M"){
        return "MARIN";
    }
    return "";
}


int main() {
    list<string> cars {"V", "M", "S"};
    string a,b;
    cin >> a;
    cin >> b;
    int ind1 = index(a, cars);
    int ind2 = index(b, cars);

    if(ind1<ind2){
        cout << getname(a);
    } else {
        cout << getname(b);
    }
}
