# openEuler 虚拟机命令速查表

> 整理时间：2026-09-11
> 环境：Windows + VMware 17.6.4 + openEuler 24.03 LTS SP1（无桌面最小安装）
> 连接方式：Windows PowerShell 通过 SSH 连接 `root@192.168.10.128`

---

## 一、Windows 侧命令（在 PowerShell 里执行）

| 命令 | 作用 | 备注 |
|------|------|------|
| `Win + R` → `powershell` | 打开 PowerShell | 也可 Win 键搜 powershell |
| `ssh root@192.168.10.128` | 登录虚拟机 | 首次连问 yes；密码输入不显示 |
| `exit` | 断开 SSH，回到 Windows | 提示符从 `[root@...]#` 变回 `PS C:\>` |
| `scp -r 本地目录 root@IP:/远程路径` | 整个文件夹传到虚拟机 | 中文路径会乱码，先 cd 用相对路径 |
| `scp 文件 root@IP:/远程目录/` | 单个文件传到虚拟机 | 例：传 ghuffmantree.cpp |
| `cd "路径"` | 切换当前目录 | Tab 键可自动补全 |
| `ls` | 列出当前目录文件 | 等价于 dir |
| `pwd` | 看当前所在目录 | print working directory |
| `Ctrl + V` / 鼠标右键 | 粘贴到 PowerShell 窗口 | 新版终端 Ctrl+V，老版右键 |

> **判断自己在哪边**：
> - `PS C:\Users\ASDE>` → Windows 本机
> - `[root@localhost ~]#` → 虚拟机内部

---

## 二、Linux 侧命令（SSH 登录后在虚拟机里执行）

### 1. 系统信息与环境判断

| 命令 | 作用 |
|------|------|
| `systemctl get-default` | 查默认启动模式：`multi-user.target`=无桌面，`graphical.target`=有桌面 |
| `ip addr \| grep "inet 192"` | 查虚拟机 IP 地址（找 ens33 那行） |
| `whoami` | 查当前登录用户名 |
| `cat /etc/passwd \| grep bash` | 列出系统里可登录的普通用户 |
| `uname -a` | 查看内核版本信息 |

### 2. 关机 / 重启

| 命令 | 作用 |
|------|------|
| `sudo poweroff` | 关机 |
| `sudo reboot` | 重启 |
| `exit` | 只退出当前终端（不关机） |

### 3. 换软件源（清华大学镜像）

| 命令 | 作用 |
|------|------|
| `sudo cp /etc/yum.repos.d/openEuler.repo /etc/yum.repos.d/openEuler.repo.bak` | 备份原源配置 |
| `sudo sed -i 's\|repo.openeuler.org\|mirrors.tuna.tsinghua.edu.cn/openeuler\|g' /etc/yum.repos.d/openEuler.repo` | 把官方源替换为清华镜像 |
| `sudo dnf clean all && sudo dnf makecache` | 清缓存并重建索引，验证源可用 |

### 4. 安装 / 查看软件（dnf 包管理）

| 命令 | 作用 |
|------|------|
| `sudo dnf install -y 包名` | 安装软件（-y 自动确认） |
| `sudo dnf install -y gcc gcc-c++ gdb make git vim cmake` | 一次装齐 C++ 开发工具链 |
| `sudo dnf remove 包名` | 卸载软件 |
| `rpm -qa \| grep 关键词` | 查某软件是否已安装 |
| `g++ --version` | 查看编译器版本（同理 gcc/gdb/git/make） |

**已装工具链**：gcc/g++ 12.3.1、gdb 14.1、git 2.43.0、make、vim、cmake

### 5. SSH 服务（让 Windows 能连进来）

| 命令 | 作用 |
|------|------|
| `sudo dnf install -y openssh-server` | 安装 SSH 服务端 |
| `sudo systemctl enable --now sshd` | 启动 SSH 服务并设为开机自启 |
| `systemctl status sshd` | 查看 SSH 服务运行状态 |

### 6. 文件与目录操作

| 命令 | 作用 |
|------|------|
| `ls -lh` | 列出文件（-l 详情，-h 易读大小） |
| `cd 目录` / `cd ..` / `cd ~` | 进入目录 / 上一级 / 家目录 |
| `pwd` | 显示当前路径 |
| `mkdir -p ~/hello` | 创建目录（-p 自动建父目录） |
| `cp 源 目标` / `mv 源 目标` / `rm 文件` | 复制 / 移动改名 / 删除 |
| `find . -name "*.cpp"` | 按名称查找文件 |
| `cat > 文件 << 'EOF' ... EOF` | 一次性写入多行文件内容（heredoc） |
| `diff 文件1 文件2` | 逐字节比较两个文件是否相同 |

### 7. 编译与运行（C++）

| 命令 | 作用 |
|------|------|
| `g++ -std=c++17 源文件.cpp -o 程序名` | 编译 C++（Linux 用 g++，Windows 用 cl.exe） |
| `./程序名` | 运行当前目录下的可执行文件（`./`=当前目录） |
| `ls -lh huffman` | 确认编译产物生成（绿色带 x = 可执行） |
| `diff 原文件 解压文件 && echo "验证通过"` | 压缩/解压结果正确性验证 |

**本次哈夫曼项目实操**：

```bash
cd /root/huffman
g++ -std=c++17 main.cpp ghuffmantree.cpp -o huffman
./huffman
diff gbintree.h gbintree_hfm.h && echo "===== 解压验证通过 ====="
```

---

## 三、字符与符号的含义

| 符号 | 含义 |
|------|------|
| `#` | root（超级用户）提示符 |
| `$` | 普通用户提示符 |
| `~` | 家目录（root 用户是 `/root`） |
| `./` | 当前目录 |
| `\|` | 管道：把前一个命令的输出交给后一个命令 |
| `&&` | 前一条成功才执行后一条 |
| `-y` | 自动回答 yes（免交互） |

---

## 四、踩坑备忘（重要）

| 坑 | 现象 | 解法 |
|----|------|------|
| 中文路径传参 | `scp: stat local ... No such file or directory` | 源码路径一律用英文；或先 cd 再传相对路径 |
| 编译"没反应" | g++ 敲完直接回提示符 | **Linux 无消息 = 成功**，报错才会输出 |
| 段错误 | `Segmentation fault (核心已转储)` | 多为空指针/越界；本次是 `create()` 未实现导致 |
| 剪贴板失效 | 无桌面环境自然没有剪贴板 | 用 SSH 在 Windows 侧操作，粘贴用 Ctrl+V / 右键 |
| IP 变化 | 连不上虚拟机 | 虚拟机内 `ip addr \| grep "inet 192"` 重查 |

---

## 五、常用连接流程（一句话版）

```
Windows PowerShell → ssh root@192.168.10.128 → 干活 → exit
传文件：scp -r 本地路径 root@192.168.10.128:/root/目标目录
```
