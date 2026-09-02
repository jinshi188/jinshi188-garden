#include <iostream>
#include <cstdlib>
#include <windows.h>   // 控制台 UTF-8 编码
using namespace std;

// 线性顺序表（动态分配版本）
typedef int ElemType;

struct SeqList {
    ElemType* data;   // 存储数组基地址
    int length;       // 当前元素个数
    int maxSize;      // 最大容量
};

// —— 初始化 ——
void InitList(SeqList& L, int size = 100) {
    L.data = new ElemType[size];
    if (!L.data) { cerr << "内存分配失败\n"; exit(1); }
    L.length  = 0;
    L.maxSize = size;
}

// —— 销毁 ——
void DestroyList(SeqList& L) {
    delete[] L.data;
    L.data    = nullptr;
    L.length  = 0;
    L.maxSize = 0;
}

// —— 判空 ——
bool ListEmpty(const SeqList& L) {
    return L.length == 0;
}

// —— 求长度 ——
int ListLength(const SeqList& L) {
    return L.length;
}

// —— 按位序取值（1 ≤ i ≤ length） ——
bool GetElem(const SeqList& L, int i, ElemType& e) {
    if (i < 1 || i > L.length) return false;
    e = L.data[i - 1];
    return true;
}

// —— 按值查找，返回位序（1起），未找到返回 0 ——
int LocateElem(const SeqList& L, ElemType e) {
    for (int i = 0; i < L.length; i++)
        if (L.data[i] == e) return i + 1;
    return 0;
}

// —— 插入：在第 i 个位置插入 e（1 ≤ i ≤ length+1） ——
bool ListInsert(SeqList& L, int i, ElemType e) {
    if (i < 1 || i > L.length + 1) return false;  // 位置非法
    if (L.length >= L.maxSize)      return false;  // 表满

    // 第 i 个位置之后的元素后移
    for (int j = L.length; j >= i; j--)
        L.data[j] = L.data[j - 1];

    L.data[i - 1] = e;
    L.length++;
    return true;
}

// —— 删除：删除第 i 个元素，用 e 返回其值 ——
bool ListDelete(SeqList& L, int i, ElemType& e) {
    if (i < 1 || i > L.length) return false;       // 位置非法

    e = L.data[i - 1];
    // 第 i 个位置之后的元素前移
    for (int j = i; j < L.length; j++)
        L.data[j - 1] = L.data[j];

    L.length--;
    return true;
}

// —— 遍历输出 ——
void PrintList(const SeqList& L) {
    for (int i = 0; i < L.length; i++)
        cout << L.data[i] << (i < L.length - 1 ? " " : "");
    cout << "\n";
}

// ===== 测试主函数 =====
int main() {
    SetConsoleOutputCP(CP_UTF8);   // 设置控制台 UTF-8 输出
    SeqList L;
    InitList(L, 10);

    // 构建顺序表：尾插 5 个元素
    cout << "=== 插入元素 ===\n";
    for (int v : {12, 35, 78, 90, 56})
        ListInsert(L, L.length + 1, v);   // 始终在末尾插
    PrintList(L);                          // 12 35 78 90 56

    // 在第 3 个位置插入 42
    cout << "=== 在第3位插入42 ===\n";
    ListInsert(L, 3, 42);
    PrintList(L);                          // 12 35 42 78 90 56

    // 按值查找
    cout << "=== 查找78的位序 ===\n";
    cout << LocateElem(L, 78) << "\n";     // 5

    // 按位序取值
    ElemType e;
    GetElem(L, 2, e);
    cout << "=== 第2个元素 ===\n" << e << "\n";  // 35

    // 删除第 4 个元素
    cout << "=== 删除第4个元素 ===\n";
    ListDelete(L, 4, e);
    cout << "删除了: " << e << "\n";       // 78
    PrintList(L);                          // 12 35 42 90 56

    cout << "表长: " << ListLength(L) << "\n";
    cout << "是否为空: " << (ListEmpty(L) ? "是" : "否") << "\n";

    DestroyList(L);
    return 0;
}
