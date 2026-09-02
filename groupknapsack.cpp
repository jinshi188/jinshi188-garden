#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int m, n;
    // m = capacity, n = number of groups
    while (cin >> m >> n) {
        // v[i][j]: value of item j in group i
        vector<vector<int>> v(n + 1, vector<int>(m + 1, 0));
        for (int i = 1; i <= n; ++i) {
            for (int j = 1; j <= m; ++j) {
                cin >> v[i][j];
            }
        }

        // dp[i][j]: max value using first i groups with capacity j
        vector<vector<int>> dp(n + 1, vector<int>(m + 1, 0));

        for (int i = 1; i <= n; ++i) {
            for (int j = 0; j <= m; ++j) {
                dp[i][j] = dp[i - 1][j];
                for (int x = 1; x <= j; ++x) {
                    dp[i][j] = max(dp[i][j], dp[i - 1][j - x] + v[i][x]);
                }
            }
        }

        cout << dp[n][m] << endl;
    }
    return 0;
}
