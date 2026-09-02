# -*- coding: utf-8 -*-
import time
import pyautogui
import pyttsx3
import pyperclip

# ===================== 配置 =====================
DEBUG = True          # 是否打印调试日志
USE_VOICE = False     # 是否启用语音播报（默认关闭，避免吵闹）

# 模板匹配置信度（0.0~1.0），可手动调整
CONF = {
    "qq_icon": 0.7,
    "target_chat": 0.7,
    "input_box": 0.65,
    "send_btn": 0.7,
}

# 模板图片路径
qq_icon = "assets/qq_icon.png"
send_btn = "assets/send_btn.png"
input_box = "assets/input_area.png"
target_chat = "assets/target_chat.png"  # 宁龙宇聊天窗口标题栏

# 自动回复内容
reply = "收到！"

# 冷却时间（秒），防止刷屏
COOLDOWN = 5
last_reply_time = 0

# ===================== 工具函数 =====================
def log(msg):
    if DEBUG:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

try:
    engine = pyttsx3.init()
except Exception as e:
    engine = None
    log(f"[警告] 语音引擎初始化失败: {e}")

def speak(text):
    log(f"[语音] {text}")
    if USE_VOICE and engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            log(f"[语音错误] {e}")

def find(img, confidence=0.8, region=None):
    """在屏幕上查找模板图片中心点"""
    try:
        pos = pyautogui.locateCenterOnScreen(img, confidence=confidence, region=region)
        return pos
    except Exception:
        return None

def send_reply():
    """清空输入框、粘贴回复并发送"""
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")
    pyperclip.copy(reply)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    # 优先用回车发送，避免发送按钮误识别
    pyautogui.press("enter")
    log(f"[发送] 已回复: {reply}")

def on_cooldown():
    """检查是否处于冷却期"""
    return time.time() - last_reply_time < COOLDOWN

# ===================== 两种回复场景 =====================
def reply_in_active_chat():
    """场景 A：聊天窗口已经打开并可见"""
    global last_reply_time
    if on_cooldown():
        return False

    # 先检测目标聊天标题栏
    chat_pos = find(target_chat, confidence=CONF["target_chat"])
    if not chat_pos:
        return False

    log(f"[匹配] 目标聊天窗口: {chat_pos}")

    # 检测输入框
    inp = find(input_box, confidence=CONF["input_box"])
    if not inp:
        log("[跳过] 未找到输入框")
        return False

    log(f"[匹配] 输入框: {inp}")
    pyautogui.moveTo(inp, duration=0.3)
    pyautogui.click()
    send_reply()
    last_reply_time = time.time()
    speak("消息已发送")
    return True

def reply_from_notification():
    """场景 B：任务栏收到新消息，从图标进入"""
    global last_reply_time
    if on_cooldown():
        return False

    icon = find(qq_icon, confidence=CONF["qq_icon"])
    if not icon:
        return False

    log(f"[匹配] QQ 消息图标: {icon}")
    speak("有新的消息")
    pyautogui.moveTo(icon, duration=0.3)
    pyautogui.click()
    time.sleep(2)

    # 检查是否为目标聊天
    chat_pos = find(target_chat, confidence=CONF["target_chat"])
    if not chat_pos:
        log("[跳过] 不是目标聊天，关闭窗口")
        pyautogui.hotkey("ctrl", "w")
        return False

    log("[通过] 是目标聊天")
    inp = find(input_box, confidence=CONF["input_box"])
    if not inp:
        log("[跳过] 未找到输入框，关闭窗口")
        pyautogui.hotkey("ctrl", "w")
        return False

    log(f"[匹配] 输入框: {inp}")
    pyautogui.moveTo(inp, duration=0.3)
    pyautogui.click()
    send_reply()

    # 发送完关闭窗口
    time.sleep(1)
    pyautogui.hotkey("ctrl", "w")
    last_reply_time = time.time()
    speak("消息已发送")
    return True

# ===================== 主程序 =====================
if __name__ == "__main__":
    log("=== QQ 自动回复脚本 ===")
    log("按 Ctrl+C 或把鼠标移到屏幕左上角可停止")
    log(f"自动回复内容: {reply}")
    log("模式：检测已打开的聊天窗口 + 检测任务栏新消息")
    speak("QQ自动回复已启动")

    try:
        while True:
            time.sleep(1)
            # 优先处理已打开的聊天窗口
            if reply_in_active_chat():
                continue
            # 再处理任务栏通知
            if reply_from_notification():
                continue
            log("未检测到目标聊天，继续监听...")
    except KeyboardInterrupt:
        log("\n[信息] 用户中断，正在停止...")
        speak("已停止")
    except Exception as e:
        log(f"\n[错误] 脚本异常: {e}")
        speak("脚本发生错误")
