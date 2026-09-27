#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KataHex 2025 人机对弈客户端（GTP）
===================================
作用：命令行跑 Hex 人机对弈。你执黑(●)，KataHex 执白(○)。

引擎：D:\\KataHex_20250131\\engine\\hex19x_opencl.exe   （支持 <=19x19）
配置：D:\\KataHex_20250131\\engine.cfg
模型：D:\\KataHex_20250131\\weights\\hex3_27x_b28.bin.gz（b28c512n，2025-01-31）

用法：
    python katahex_gtp.py              # 11x11，每步 500 次模拟
    python katahex_gtp.py 13           # 13x13
    python katahex_gtp.py 19 800       # 19x19，每步 800 次模拟
    python katahex_gtp.py 11 0         # maxVisits=0 表示不限（很慢，慎用）

输入坐标：列字母 + 行号（如 d4、K10、j16；行号 1 在最下）。列字母跳过 I，
         和引擎 showboard 打印的头一行完全一致。
其他输入： q 退出 / pass 弃权 / board 重印棋盘

【重要·坐标转换】
这个 KataHex 引擎**不认**标准围棋坐标（play b d4 会被拒绝）。它内部用"扩展
网格"坐标 (a,b)，映射关系（N = 棋盘路数；C 为 0 起列号 A=0 并跳过 I；D 为
showboard 打印的行号 1..N，1 在最下；内部 y 从顶部数，y = N-D）：
    (C,D) -> (a,b) :  a = 2*C - D + (N+1)     b = (2N+1) - 2*D
    (a,b) -> (C,D) :  D = ((2N+1) - b)/2      C = (a - (N+1) + D)/2
例（19 路）：中腹 (C=9,D=10) -> (28,19)；四角 (C0,D19)->(1,1) / (C18,D1)->(55,37)。
（公式已 361 格全盘实测通过，来源为 HZY 源码 Location::tryOfString）

引擎 genmove/analyze **输出**的是字母格式顶点（如 AK32 / X8）。它只是同一对
(a,b) 的另一种写法（源码 Location::toString）：
    a 用 25 字母表（跳过 I）编码 -> x_print；数字部分 = 2N+1-b
例如 AK32 == (a,b)=(34,7) == (C=15,D=16)；X8 == (22,31) == (C=3,D=4)。
本程序直接解码它得到落子格；若解码异常，再退回 showboard 前后差兜底。
"""

import os
import re
import subprocess
import sys
import threading
import time

# ================= 只改这里是 2025 套路径 =================
ROOT    = r"D:\KataHex_20250131"                 # 2025 完整包根目录
BACKEND = "opencl"                               # opencl / cuda（tensorrt 不支持本机显卡）
ENGINE  = os.path.join(ROOT, "engine", "hex19x_" + BACKEND + ".exe")
CONFIG  = os.path.join(ROOT, "engine.cfg")
MODEL   = os.path.join(ROOT, "weights", "hex3_27x_b28.bin.gz")
WORKDIR = ROOT                                   # 引擎日志/缓存写在这里

BOARD      = 11       # 棋盘大小，默认 11x11
MAX_VISITS = 500      # 每步模拟次数：越大越强越慢；0 = 不限
# =========================================================

# 命令行覆盖： python katahex_gtp.py <棋盘大小> [每步模拟数]
if len(sys.argv) > 1:
    try:
        BOARD = int(sys.argv[1])
    except ValueError:
        pass
if len(sys.argv) > 2:
    try:
        MAX_VISITS = int(sys.argv[2])
    except ValueError:
        pass

# 列字母（跳过 I，围棋习惯）：A B C D E F G H J K L M N O P Q R S T U V W X Y Z
COLS = "ABCDEFGHJKLMNOPQRSTUVWXYZ"

# 引擎顶点用的 25 字母表（源码里的 xChar，同样跳过 I）
XCHAR = "ABCDEFGHJKLMNOPQRSTUVWXYZ"

STARTUP_NOISE = (
    "Creating context", "Using OpenCL Device", "Loaded tuning", "Initializing board",
    "WARNING", "Unused key", "----", "Loaded config", "Loaded model", "Model name",
    "GTP ready", "KataGo v", "Using Tromp", "Found OpenCL", "nnRandSeed",
    "After dedups", "Dummy tuning", "Done tuning", "OpenCL backend",
)


def preflight():
    """启动前先查文件在不在，缺了直接说清楚。"""
    problems = []
    for label, path in (("引擎", ENGINE), ("配置", CONFIG), ("模型", MODEL)):
        if not os.path.exists(path):
            problems.append("  缺 %s: %s" % (label, path))
    if problems:
        print("找不到 2025 套的文件：")
        print("\n".join(problems))
        print("\n检查 D:\\KataHex_20250131 是否完整（应有 engine\\ 和 weights\\ 两个目录）。")
        sys.exit(1)
    if BACKEND == "tensorrt":
        print("提示：tensorrt 后端在 RTX 50 系（Blackwell）上会崩溃，改用 opencl 或 cuda。")
    if not (1 <= BOARD <= 19):
        print("棋盘大小要在 1..19 之间（hex19x 引擎上限）。")
        sys.exit(1)


# ==================== 坐标转换 ====================
def cell_to_engine(C, D, N):
    """(列C 0起, 行D 1起) -> 引擎扩展坐标 (a, b)"""
    return 2 * C - D + (N + 1), (2 * N + 1) - 2 * D


def engine_to_cell(a, b, N):
    """引擎扩展坐标 (a, b) -> (列C, 行D)；不在棋盘上返回 None"""
    t = (2 * N + 1) - b
    if t % 2:
        return None
    D = t // 2
    u = a - (N + 1) + D
    if u % 2:
        return None
    C = u // 2
    if 0 <= C < N and 1 <= D <= N:
        return C, D
    return None


def cell_to_str(C, D):
    return "%s%d" % (COLS[C], D)


def vertex_to_cell(v, N):
    """引擎输出的字母顶点（AK32 / X8 / AV10 ...）-> (C, D)；解析失败返回 None。

    对应源码 Location::toString：
        x_print = 2*x + y + 1 ,  y = N - D   (= 我们的 a)
        数字部分 = 2*(N - y) = 2*D
        x_print 用 25 字母表编码（单字母时直接是下标，双字母时 (i0+1)*25+i1）
    """
    if not v:
        return None
    s = v.strip().upper()
    if s in ("PASS", "RESIGN", "NULL"):
        return None
    m = re.match(r"^([A-Z]+)(\d+)$", s)
    if not m:
        return None
    letters, num = m.group(1), int(m.group(2))
    if any(ch not in XCHAR for ch in letters) or len(letters) > 2:
        return None
    idx = [XCHAR.index(ch) for ch in letters]
    x_print = idx[0] if len(idx) == 1 else (idx[0] + 1) * 25 + idx[1]
    if num % 2:
        return None
    D = num // 2
    y = N - D
    u = x_print - 1 - y
    if u % 2:
        return None
    C = u // 2
    if 0 <= C < N and 1 <= D <= N:
        return C, D
    return None


def str_to_cell(s, N):
    """用户输入 'd4' / 'K10' -> (C, D)，不合法返回 None"""
    s = s.strip().upper().replace(" ", "")
    m = re.match(r"^([A-Z])(\d{1,2})$", s)
    if not m:
        return None
    letter, digits = m.group(1), m.group(2)
    if letter not in COLS[:N]:
        return None
    C = COLS.index(letter)
    D = int(digits)
    if not (1 <= D <= N):
        return None
    return C, D


def parse_board(blk):
    """把 showboard 的多行输出解析成 {(C, D): 'X'/'O'}

    每个格子固定 2 字符：空格 '. '、普通子 'X '、最近几手带序号 'X1'（序号
    顶掉填充空格，宽度不变）。所以一律每格前进 2。仅作兜底用，主路径靠
    vertex_to_cell()，更稳的兜底是 printsgf。
    """
    grid = {}
    for ln in blk:
        m = re.match(r"^\s*(\d+)\s(.*)$", ln)
        if not m:
            continue
        row = int(m.group(1))
        content = m.group(2)
        for k in range(len(content) // 2):
            ch = content[2 * k]
            if ch in "XO":
                grid[(k, row)] = ch
    return grid


def sgf_last_cell(sgf_text, N):
    """从 printsgf 的 SGF 文本里取最后一手的 (C, D)。

    SGF 顶点是两字母：第 1 个是列(a=0)，第 2 个是从顶部数的行(a=0)。
    """
    ms = re.findall(r"[BW]\[([a-z]{2})\]", sgf_text)
    if not ms:
        return None
    s = ms[-1]
    C = ord(s[0]) - ord("a")
    row_from_top = ord(s[1]) - ord("a")
    D = N - row_from_top
    if 0 <= C < N and 1 <= D <= N:
        return C, D
    return None


def sgf_last_color(sgf_text):
    """printsgf 文本里最后一手的颜色 'B'/'W'；没有则返回 None。"""
    ms = re.findall(r"([BW])\[([a-z]*)\]", sgf_text)
    if not ms:
        return None
    return ms[-1][0]


# ==================== GTP 客户端 ====================
class GtpEngine(object):
    """极简 GTP 客户端：写 stdin，读 stdout（用线程读，便于超时控制）。"""

    def __init__(self, exe, config, model, cwd):
        self.proc = subprocess.Popen(
            [exe, "gtp", "-config", config, "-model", model],
            cwd=cwd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,          # 引擎日志也收进来，方便看状态
            text=True, encoding="utf-8", errors="replace",
            bufsize=1,
        )
        self._lines = []
        self._lock = threading.Lock()
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        for ln in self.proc.stdout:
            with self._lock:
                self._lines.append(ln.rstrip("\n"))

    def send(self, cmd, wait=180.0):
        """发一条 GTP 命令，等回复结束（GTP 回复以空行收尾）。"""
        with self._lock:
            before = len(self._lines)
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()
        t0 = time.time()
        got = []
        started = 0.0
        while time.time() - t0 < wait:
            time.sleep(0.03)
            with self._lock:
                got = self._lines[before:]
            if started <= 0:
                if got and any(g.startswith("=") or g.startswith("?") for g in got):
                    started = time.time()
                continue
            # 已经看到回复起始行：等一个空行收尾，或最多再等 1s
            i0 = 0
            for i, g in enumerate(got):
                if g.startswith("=") or g.startswith("?"):
                    i0 = i
                    break
            if any(g.strip() == "" for g in got[i0:]) or (time.time() - started) > 1.0:
                break
        return [g for g in got if g and not g.startswith(STARTUP_NOISE)]

    def close(self):
        try:
            self.proc.stdin.write("quit\n")
            self.proc.stdin.flush()
            self.proc.wait(timeout=8)
        except Exception:
            try:
                self.proc.terminate()
            except Exception:
                pass


def main():
    preflight()
    size_mb = os.path.getsize(MODEL) // (1024 * 1024) if os.path.exists(MODEL) else 0
    print("正在启动 KataHex 2025 引擎（%dMB 模型，第一次要十几秒，请稍等）..." % size_mb)
    eng = GtpEngine(ENGINE, CONFIG, MODEL, WORKDIR)

    N = BOARD
    r = eng.send("boardsize %d" % N, wait=300)
    if r and r[0].startswith("?"):
        print("boardsize 失败：%s" % r[0])
        eng.close()
        sys.exit(1)
    eng.send("clear_board")
    eng.send("komi 0")
    if MAX_VISITS > 0:
        eng.send("kata-set-param maxVisits %d" % MAX_VISITS)

    print("\n===== 对局开始：你执黑(●)，KataHex 2025 执白(○) =====")
    print("     棋盘 %dx%d，每步 %s 次模拟（后端 %s）"
          % (N, N, MAX_VISITS if MAX_VISITS > 0 else "不限", BACKEND))
    print("     输入坐标如 d4 / K10（列字母跳过 I，行号 1 在最下）；q 退出")

    passes = 0
    while True:
        print("\n--- 当前棋盘 ---")
        print("\n".join(eng.send("showboard")))

        raw = input("\n轮到你(黑)走，输入坐标(如 d4)：").strip()
        if raw.lower() in ("q", "quit", "exit"):
            print("已退出。")
            break
        if raw.lower() == "board":
            continue
        if raw.lower() == "pass":
            r = eng.send("play b pass")
            if not r or not r[0].startswith("="):
                print("  → 弃权未被接受：%s" % (r[0] if r else "无回复"))
                continue
            passes += 1
            print("  你选择弃权。")
        else:
            cell = str_to_cell(raw, N)
            if cell is None:
                print("  → 坐标看不懂，示例：d4 / K10（列跳过 I，行 1-%d）" % N)
                continue
            C, D = cell
            a, b = cell_to_engine(C, D, N)
            r = eng.send("play b (%d,%d)" % (a, b))
            if not r or not r[0].startswith("="):
                print("  → 该点不合法或已被占（引擎：%s），重来。" % (r[0] if r else "无回复"))
                continue
            passes = 0

        print("KataHex(白)思考中...")
        resp = eng.send("genmove w", wait=1800)
        head = resp[0].lstrip("= ").strip() if resp else ""
        if (not head) or (resp and resp[0].startswith("?")) or head.lower() == "resign":
            print("（引擎认输/无回复：%s，本局结束）" % (head or "无回复"))
            break
        v = head

        if v.lower() == "pass":
            print("KataHex 走：pass（弃权）")
            passes += 1
            if passes >= 2:
                print("\n双方连续弃权，本局结束。")
                break
            continue
        passes = 0

        # ★ 这个引擎的 genmove 会把子直接落到盘上（KataGo GTP 的行为），
        #   所以这里不能再去 play 一次。用 printsgf 确认它确实落了。
        sgf = " ".join(eng.send("printsgf"))
        if sgf_last_color(sgf) != "W":
            # 没落上 → 自己补一手（原样顶点优先，其次按公式解出的数字形式）
            played = eng.send("play w %s" % v)
            if played and played[0].startswith("?"):
                cell = vertex_to_cell(v, N)
                if cell is not None:
                    a, b = cell_to_engine(cell[0], cell[1], N)
                    played = eng.send("play w (%d,%d)" % (a, b))
            if played and played[0].startswith("?"):
                print("（引擎的应手无法落子：顶点 %s / %s，本局结束）" % (v, played[0]))
                break
            sgf = " ".join(eng.send("printsgf"))

        cell = sgf_last_cell(sgf, N) or vertex_to_cell(v, N)
        if cell is not None:
            print("KataHex 走：%s   （引擎顶点 %s）" % (cell_to_str(cell[0], cell[1]), v))
        else:
            print("KataHex 走：%s   （未能自动定位，请照棋盘看）" % v)

    eng.close()
    print("\n对局结束。")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print("启动失败，找不到文件：%s" % e)
        sys.exit(1)
    except EOFError:
        print("\n输入结束，退出。")
    except KeyboardInterrupt:
        print("\n中断退出。")
