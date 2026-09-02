#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

const int MOD = 100000;

// 用两个 unsigned long long 模拟 128 位整数（低64位 + 高64位）
// 因为 2^499 需要 500 位，用更通用的方案：
// 由于 2^K 单调递增，dist 最大不超过 N * 2^(M-1)
// M <= 500, N <= 500, 所以最多 500 * 2^499
// 需要真正的大整数。这里用 vector<uint64_t> 表示大数（base 2^63）

struct BigInt {
    // 用 base 10^9 存储，方便取模和比较
    vector<long long> d; // d[0] 是最低位，base=10^9
    static const long long BASE = 1000000000LL;
    bool is_inf;

    BigInt() : is_inf(false) {}
    BigInt(bool inf) : is_inf(inf) {}
    BigInt(long long v) : is_inf(false) {
        if (v > 0) d.push_back(v % BASE);
        if (v >= BASE) d.push_back(v / BASE);
    }

    bool operator<(const BigInt& o) const {
        if (is_inf && o.is_inf) return false;
        if (is_inf) return false;
        if (o.is_inf) return true;
        if (d.size() != o.d.size()) return d.size() < o.d.size();
        for (int i = (int)d.size()-1; i >= 0; i--)
            if (d[i] != o.d[i]) return d[i] < o.d[i];
        return false;
    }
    bool operator>(const BigInt& o) const { return o < *this; }
    bool operator==(const BigInt& o) const {
        if (is_inf != o.is_inf) return false;
        return d == o.d;
    }
    bool operator<=(const BigInt& o) const { return !(o < *this); }

    BigInt operator+(const BigInt& o) const {
        if (is_inf || o.is_inf) return BigInt(true);
        BigInt res;
        long long carry = 0;
        int n = max(d.size(), o.d.size());
        for (int i = 0; i < n || carry; i++) {
            long long cur = carry;
            if (i < (int)d.size()) cur += d[i];
            if (i < (int)o.d.size()) cur += o.d[i];
            res.d.push_back(cur % BASE);
            carry = cur / BASE;
        }
        return res;
    }

    long long mod(long long m) const {
        if (is_inf) return -1;
        long long res = 0, base = 1;
        for (int i = 0; i < (int)d.size(); i++) {
            res = (res + (d[i] % m) * (base % m)) % m;
            base = (base * (BASE % m)) % m;
        }
        return res;
    }
};

// 计算 2^k 作为 BigInt
BigInt pow2(int k) {
    BigInt res(1LL);
    BigInt two(2LL);
    // 快速幂
    // 这里用简单循环，k<=499 可接受
    for (int i = 0; i < k; i++) {
        BigInt next;
        long long carry = 0;
        for (int j = 0; j < (int)res.d.size() || carry; j++) {
            long long cur = carry;
            if (j < (int)res.d.size()) cur += res.d[j] * 2;
            next.d.push_back(cur % BigInt::BASE);
            carry = cur / BigInt::BASE;
        }
        res = next;
    }
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, M;
    cin >> N >> M;

    vector<vector<pair<int, int>>> adj(N); // {neighbor, edge_index}

    for (int k = 0; k < M; k++) {
        int u, v;
        cin >> u >> v;
        adj[u].push_back({v, k});
        adj[v].push_back({u, k});
    }

    // 预计算所有边权 2^k
    vector<BigInt> w(M);
    for (int k = 0; k < M; k++) w[k] = pow2(k);

    // Dijkstra，用 BigInt 作为距离
    // 由于 BigInt 比较开销大，优先队列改用自定义比较
    vector<BigInt> dist(N, BigInt(true)); // INF
    dist[0] = BigInt(0LL);

    // priority_queue with custom comparator
    // pair<BigInt, int>，小顶堆
    using T = pair<BigInt, int>;
    auto cmp = [](const T& a, const T& b) { return a.first > b.first; };
    priority_queue<T, vector<T>, decltype(cmp)> pq(cmp);
    pq.push({BigInt(0LL), 0});

    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto [v, k] : adj[u]) {
            BigInt nd = dist[u] + w[k];
            if (nd < dist[v]) {
                dist[v] = nd;
                pq.push({dist[v], v});
            }
        }
    }

    for (int i = 1; i < N; i++) {
        if (dist[i].is_inf)
            cout << -1 << "\n";
        else
            cout << dist[i].mod(MOD) << "\n";
    }

    return 0;
}
