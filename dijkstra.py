import heapq
import sys

def solve():
    input_data = sys.stdin.read().split()
    idx = 0
    N = int(input_data[idx]); idx += 1
    M = int(input_data[idx]); idx += 1

    adj = [[] for _ in range(N)]
    for k in range(M):
        u = int(input_data[idx]); idx += 1
        v = int(input_data[idx]); idx += 1
        w = 1 << k  # 2^k，Python 支持大整数
        adj[u].append((v, w))
        adj[v].append((u, w))

    INF = float('inf')
    dist = [INF] * N
    dist[0] = 0
    pq = [(0, 0)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))

    MOD = 100000
    for i in range(1, N):
        if dist[i] == INF:
            print(-1)
        else:
            print(dist[i] % MOD)

solve()
