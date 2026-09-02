#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int m, n;
    while (cin >> m >> n) {
        // V[x][i]: x 十万元投入第 i 个地区的脱贫人数
        vector<vector<int>> V(m + 1, vector<int>(n + 1, 0));
        for (int x = 1; x <= m; ++x)
            for (int i = 1; i <= n; ++i)
                cin >> V[x][i];

        // dp[j]: 容量 j 时的最大价值（滚动数组）
        vector<int> dp(m + 1, 0);

        // dec[i][j]: 第 i 个地区分配了多少（用于回溯）
        vector<vector<int>> dec(n + 1, vector<int>(m + 1, 0));

        for (int i = 1; i <= n; ++i) {
            // 分组背包：j 必须逆序遍历
            for (int j = m; j >= 0; --j) {
                int best = dp[j];       // 不选第 i 组
                int bestx = 0;
                for (int x = 1; x <= j; ++x) {
                    int val = dp[j - x] + V[x][i];
                    if (val > best) {
                        best = val;
                        bestx = x;
                    }
                }
                dp[j] = best;
                dec[i][j] = bestx;
            }
        }

        cout << dp[m] << endl;

        // 回溯分配方案
        vector<int> alloc(n + 1, 0);
        int remain = m;
        for (int i = n; i >= 1; --i) {
            alloc[i] = dec[i][remain];
            remain -= alloc[i];
        }

        for (int i = 1; i <= n; ++i) {
            cout << alloc[i];
            if (i < n) cout << " ";
        }
        cout << endl;
    }
    return 0;
}
