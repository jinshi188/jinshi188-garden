// 计组实验：用代码验证补码 / 无符号 / 符号扩展
// 编译：cl /EHsc /std:c++17 /utf-8 int_representation.cpp
//  或：g++ -std=c++17 int_representation.cpp -o int_representation

#include <iostream>
#include <climits>
#include <iomanip>
#include <bitset>

// 把 int 的 32 位二进制打印出来
void dump(const char* label, int v) {
    // bitset 需要 unsigned 才能正确显示每一位
    std::cout << std::left << std::setw(28) << label
              << std::setw(12) << v
              << std::bitset<32>((unsigned int)v).to_string()
              << "\n";
}

int main() {
    std::cout << "========== 实验1：INT_MAX + 1 会怎样 ==========\n";
    int imax = INT_MAX;
    int overflowed = imax + 1;
    std::cout << "INT_MAX            = " << imax << "\n";
    std::cout << "INT_MAX + 1        = " << overflowed << "\n";
    std::cout << "INT_MAX + 1 == INT_MIN ? "
              << (overflowed == INT_MIN ? "true（溢出，绕回最小值）" : "false") << "\n";
    std::cout << "结论：计算机做加法不判断溢出，最高位进位直接丢弃。\n\n";

    std::cout << "========== 实验2：无符号比较陷阱 ==========\n";
    unsigned int u = 0;
    int          s = -1;
    std::cout << "u = 0u, s = -1\n";
    if (u > s)
        std::cout << "u > s 成立！（反直觉：0 > -1 居然是 true）\n";
    else
        std::cout << "u > s 不成立\n";
    std::cout << "原因：int 与 unsigned 混合运算时，int 会被强转成 unsigned，\n";
    std::cout << "      -1 变成 0xFFFFFFFF = 4294967295。\n";
    std::cout << "      (unsigned)s = " << (unsigned)s << "\n\n";

    std::cout << "========== 实验3：char 的符号扩展 ==========\n";
    char c = 0xFF;             // 8位：1111 1111
    int  i_signed   = c;                    // 有符号 char → int（符号扩展）
    unsigned char uc = 0xFF;
    int  i_unsigned = uc;                   // 无符号 char → int（零扩展）
    std::cout << "char c = 0xFF（二进制 1111 1111）\n";
    std::cout << "  (int)c            = " << i_signed   << "   ← 按最高位1补齐，变成负数\n";
    std::cout << "  (int)(unsigned)c  = " << i_unsigned << "   ← 高位补0，变成 255\n";
    std::cout << "同一串二进制，只因类型不同，解释结果完全不同。\n\n";

    std::cout << "========== 实验4：负数的补码表示 ==========\n";
    for (int v : {0, 1, -1, 2, -2, 127, -128, 255})
        dump(("v = " + std::to_string(v)).c_str(), v);
    std::cout << "\n规律：负数 = 正数按位取反再加1。\n";
    std::cout << "      所以 -1 的 32 位全是 1；-2 是 ...1110。\n\n";

    std::cout << "========== 实验5：位运算实现加减法（不用 +/- 号） ==========\n";
    auto add = [](int a, int b) {
        while (b != 0) {
            int carry = (a & b) << 1;  // 进位
            a = a ^ b;                 // 无进位相加
            b = carry;
        }
        return a;
    };
    std::cout << "8 + 5  = " << add(8, 5)  << "（应为 13）\n";
    std::cout << "8 + -5 = " << add(8, -5) << "（应为 3）\n";
    std::cout << "-8 + -5= " << add(-8,-5) << "（应为 -13）\n";
    std::cout << "原理：加法 = 异或（无进位相加）+ 与并左移（进位），循环到无进位为止。\n";

    return 0;
}
