#include <stdio.h>
#include <iostream>
#include <fstream>
#include <string.h>
#include <vector>

using namespace std;

// 分配2维数组
template <class T>
T** gAlloc2(T **&p, int n2, int n1)
{
	int i;
	size_t size = sizeof(T);
	p = new T *[n2];
	if (p == NULL) return NULL;

	p[0] = new T[n1 * n2];
	if (p[0] == NULL)
	{
		delete[] p;
		p = NULL;
		return NULL;
	}

	for (i = 0; i < n2; i++)
	{
		p[i] = p[0] + n1 * i;
	}
	return p;
}

// 释放2维数组
template <class T>
void gFree2(T **&p)
{
	delete[] p[0];
	delete[] p;
	p = NULL;
}

// 载入邻接矩阵
bool loadAdjMatrix(const char *fname, int **&mat, int &n)
{
	ifstream stream(fname, ios::in);
	if (!stream.is_open()) return false;

	int i, j;
	stream >> n;
	if (n <= 0)
	{
		stream.close();
		return false;
	}

	gAlloc2(mat, n, n);
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			stream >> mat[i][j];
		}
	}
	stream.close();
	return true;
}

// 搜索并形成关键路径表
void searchPath(const vector<int>& cpairs, vector< vector<int> > &pathList)
{
	int i, j, k;

	int m = (int)cpairs.size() / 2;
	int *refs = new int[m];
	memset(refs, 0, sizeof(int) * m);

	for (i = 0; i < m; i++)
	{
		if (refs[i] > 0) continue;

		// 添加新的路径
		pathList.insert(pathList.begin(), vector<int>());
		vector<int> &path = *pathList.begin();
		// 将当前节点对加入到路径中
		path.push_back(cpairs[i * 2]);
		path.push_back(cpairs[i * 2 + 1]);
		refs[i]++;

		// 向前搜索路径
		k = cpairs[i * 2];
		do
		{
			for (j = 0; j < m; j++)
			{
				if (k == cpairs[2 * j + 1])
				{
					k = cpairs[2 * j];
					path.insert(path.begin(), k);
					refs[j]++;
					break;
				}
			}
		} while (j < m);

		// 向后搜索路径
		k = cpairs[i * 2 + 1];
		do
		{
			for (j = 0; j < m; j++)
			{
				if (k == cpairs[2 * j])
				{
					k = cpairs[2 * j + 1];
					path.push_back(k);
					refs[j]++;
					break;
				}
			}
		} while (j < m);
	}

	delete[] refs;
}

// 计算图每个顶点的入度
void statInDegree(int **mat, int n, int *degrees)
{
	int i, j;
	memset(degrees, 0, sizeof(int) * n);
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			if (mat[j][i] != 0)
			{
				degrees[i]++;
			}
		}
	}
}

// 拓扑排序 (Kahn算法)
void topoSort(int **mat, int n, vector<int>& vs)
{
	vs.clear();
	int *degree = new int[n];
	statInDegree(mat, n, degree);

	// 用 vector 模拟队列，存放入度为0的节点
	vector<int> q;
	for (int i = 0; i < n; i++)
	{
		if (degree[i] == 0) q.push_back(i);
	}

	int head = 0;
	while (head < (int)q.size())
	{
		int v = q[head];
		head++;
		vs.push_back(v);

		// 遍历 v 的所有后继节点，将入度减1
		for (int u = 0; u < n; u++)
		{
			if (mat[v][u] != 0)
			{
				degree[u]--;
				if (degree[u] == 0) q.push_back(u);
			}
		}
	}

	delete[] degree;
}

// 计算图中各个顶点的最早发生时间
void earliest(int **mat, int n, int *topo, int *es)
{
	// 初始化为0
	for (int i = 0; i < n; i++) es[i] = 0;

	// 按拓扑顺序计算
	for (int t = 0; t < n; t++)
	{
		int v = topo[t];
		// 用 v 更新所有后继 u 的 es
		for (int u = 0; u < n; u++)
		{
			if (mat[v][u] != 0)
			{
				int new_es = es[v] + mat[v][u];
				if (new_es > es[u]) es[u] = new_es;
			}
		}
	}
}

// 计算图中各个顶点最晚结束时间
void latest(int **mat, int n, int *topo, int max_val, int *ls)
{
	// 初始化为 max_val（终点最晚时间 = 最早时间）
	for (int i = 0; i < n; i++) ls[i] = max_val;

	// 按拓扑逆序计算
	for (int t = n - 1; t >= 0; t--)
	{
		int v = topo[t];
		// 用所有后继 u 更新 ls[v]
		for (int u = 0; u < n; u++)
		{
			if (mat[v][u] != 0)
			{
				int new_ls = ls[u] - mat[v][u];
				if (new_ls < ls[v]) ls[v] = new_ls;
			}
		}
	}
}

// 关键路径算法实现
void criticalPath(int **mat, int n, vector< vector<int> > &pathList)
{
	pathList.clear();

	// Step 1: 拓扑排序
	vector<int> topo;
	topoSort(mat, n, topo);

	// Step 2: 计算最早发生时间 ve
	int *es = new int[n];
	earliest(mat, n, &topo[0], es);
	int max_es = es[topo[n - 1]];  // 终点最早时间 = 总工期

	// Step 3: 计算最晚结束时间 vl
	int *ls = new int[n];
	latest(mat, n, &topo[0], max_es, ls);

	// Step 4: 找关键活动 (e_ij == l_ij 的活动为关键活动)
	vector<int> cpairs;
	for (int i = 0; i < n; i++)
	{
		for (int j = 0; j < n; j++)
		{
			if (mat[i][j] != 0)
			{
				int e_ij = es[i];
				int l_ij = ls[j] - mat[i][j];
				if (e_ij == l_ij)
				{
					cpairs.push_back(i);
					cpairs.push_back(j);
				}
			}
		}
	}

	// Step 5: 将关键活动连接成完整路径
	searchPath(cpairs, pathList);

	// 输出调试信息
	cout << "拓扑序列: ";
	for (int i = 0; i < n; i++) cout << "v" << topo[i] << " ";
	cout << endl;

	cout << "ve: ";
	for (int i = 0; i < n; i++) cout << "v" << i << "=" << es[i] << " ";
	cout << endl;

	cout << "vl: ";
	for (int i = 0; i < n; i++) cout << "v" << i << "=" << ls[i] << " ";
	cout << endl;

	cout << "总工期 = " << max_es << endl;

	delete[] es;
	delete[] ls;
}

int main(int argc, char *argv[])
{
	int **mat;
	int n;

	// 载入邻接矩阵
	if (!loadAdjMatrix("data\\critical_path.txt", mat, n)) return -1;

	// 执行关键路径算法
	vector< vector<int> > pathList;
	criticalPath(mat, n, pathList);

	// 输出找到的关键路径
	cout << "\nCritical Path:\n";
	for (size_t i = 0; i < pathList.size(); i++)
	{
		for (size_t j = 0; j < pathList[i].size(); j++)
		{
			cout << "v" << pathList[i][j] << " ";
		}
		cout << endl;
	}

	gFree2(mat);
	return 0;
}
