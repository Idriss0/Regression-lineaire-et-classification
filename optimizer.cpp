#include <windows.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>

void optimizeProcess(DWORD pid) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) return;
    SetPriorityClass(hProcess, HIGH_PRIORITY_CLASS);
    SetProcessAffinityMask(hProcess, 0b1111);
    std::vector<int> warm(10000000, 1);
    for (auto &v : warm) v *= 2;
    CloseHandle(hProcess);
}

int main() {
    std::ifstream file("PID.dat");
    if (!file.is_open()) return 1;
    DWORD pid;
    file >> pid;
    file.close();
    optimizeProcess(pid);
    return 0;
}
