---
comments: true
---

# 最短路径问题

## Dijkstra 算法

### 过程

将结点分成两个集合：已确定最短路长度的点集（记为$S$集合）的和未确定最短路长度的点集（记为$T$集合）。一开始所有的点都属于$T$集合。

初始化 dis(s)=0，其他点的 dis 均为 $+\infty$。

然后重复这些操作：

从$T$集合中，选取一个最短路长度最小的结点，移到$S$集合中。
对那些刚刚被加入$S$集合的结点的所有出边执行松弛操作。
直到$T$集合为空，算法结束。

### 时间复杂度

有多种方法来维护 1 操作中最短路长度最小的结点，不同的实现导致了 Dijkstra 算法时间复杂度上的差异。

* 暴力：不使用任何数据结构进行维护，每次2操作执行完毕后，直接在$T$集合中暴力寻找最短路长度最小的结点。2操作总时间复杂度为$O(m)$，1操作总时间复杂度为$O(n^2)$，全过程的时间复杂度为$O(n^2 + m) = O(n^2)$。
* 优先队列：和二叉堆类似，但使用优先队列时，如果同一个点的最短路被更新多次，因为先前更新时插入的元素不能被删除，也不能被修改，只能留在优先队列中，故优先队列内的元素个数是$O(m)$的，时间复杂度为$O(m \log m)$。

!!! note "其他方法"
    * 二叉堆:每成功松弛一条边$(u,v)$，就将$v$插入二叉堆中（如果$v$已经在二叉堆中，直接修改相应元素的权值即可），1操作直接取堆顶结点即可。时间复杂度为$O((n+m) \log n) = O(m \log n)$。

    * 线段树：和二叉堆原理类似，不过将每次成功松弛后插入二叉堆的操作改为在线段树上执行单点修改，而1操作则是线段树上的全局查询最小值。时间复杂度为$O(m \log n)$。

### 实现
    
=== "暴力实现" 
      ```cpp 
        struct edge {
          int v, w;
        };

        vector<edge> e[maxn];
        int dis[maxn], vis[maxn];

        void dijkstra(int n, int s) {
          memset(dis, 63, sizeof(dis));
          dis[s] = 0;
          for (int i = 1; i <= n; i++) {
            int u = 0, mind = 0x3f3f3f3f;
            for (int j = 1; j <= n; j++)
              if (!vis[j] && dis[j] < mind) u = j, mind = dis[j];
            vis[u] = true;
            for (auto ed : e[u]) {
              int v = ed.v, w = ed.w;
              if (dis[v] > dis[u] + w) dis[v] = dis[u] + w;
            }
          }
        }
      ```
=== "优先队列实现"
     
      ```cpp
        struct edge {
          int v, w;
        };

        struct node {
          int dis, u;

          bool operator>(const node& a) const { return dis > a.dis; }
        };

        vector<edge> e[maxn];
        int dis[maxn], vis[maxn];
        priority_queue<node, vector<node>, greater<node> > q;

        void dijkstra(int n, int s) {
          memset(dis, 63, sizeof(dis));
          dis[s] = 0;
          q.push({0, s});
          while (!q.empty()) {
            int u = q.top().u;
            q.pop();
            if (vis[u]) continue;
            vis[u] = 1;
            for (auto ed : e[u]) {
              int v = ed.v, w = ed.w;
              if (dis[v] > dis[u] + w) {
                dis[v] = dis[u] + w;
                q.push({dis[v], v});
              }
            }
          }
        }
      ```