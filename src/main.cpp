#include <fstream>



int main() {
    std::ofstream out("output.txt");
    if (out.is_open()) {
        out << "Hello, World!" << std::endl;
        out.close();
    }
    return 0;
}