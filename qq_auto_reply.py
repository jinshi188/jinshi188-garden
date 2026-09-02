# -*- coding: utf-8 -*-
"""
QQ 自动回复脚本
================
功能：自动检测 QQ 消息图标，打开聊天窗口，发送预设回复，然后关闭窗口。

使用步骤：
1. 在 assets/ 目录下放置三张截图：
   - qq_icon.png    : QQ 消息提醒图标（任务栏闪烁的图标）
   - send_btn.png   : QQ 聊天窗口的发送按钮
   - input_area.png : QQ 聊天窗口的输入框区域
2. 按 Win+Shift+S 截取屏幕上对应元素，保存为 PNG。
3. 修改本文件 CONFIG 中的 auto_reply、screen_region 等参数。
4. 运行：python qq_auto_reply.py
5. 停止：按 Ctrl+C 或把鼠标快速移到屏幕左上角触发 PyAutoGUI 安全停止。

依赖：pip install pyautogui pyttsx3 opencv-python
"""

import time
import pyautogui

# 安全设置：鼠标移动到屏幕左上角 (0,0) 会触发异常，用来紧急停止
pyautogui.FAILSAFE = True

# ===================== 配置区域 =====================
CONFIG = {
    # 截图模板路径（必须存在）
    "qq_icon":    "assets/qq_icon.png",
    "send_btn":   "assets/send_btn.png",
    "input_area": "assets/input_area.png",

    # 监听屏幕区域 (x, y, width, height)
    # 设为 None 表示全屏搜索；指定区域可以加快识别速度
    # 例如：屏幕右下角区域 (1572, 1502, 988, 98)
    "screen_region": (0, 0, 2560, 1600),

    # 模板匹配置信度（0.0 ~ 1.0），越高越严格
    "confidence": 0.8,

    # 自动回复内容
    "auto_reply": "收到！",

    # 每次循环检测间隔（秒）
    "check_interval": 1,

    # 鼠标移动/点击延迟（秒）
    "click_delay": 0.5,
}


# ===================== 工具函数 =====================
def init_speaker():
    """初始化语音引擎，失败时返回 None（不影响主功能）"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        return engine
    except Exception as e:
        print(f"[警告] 语音模块初始化失败: {e}")
        return None


def speak(engine, text):
    """打印并朗读提示"""
    print(f"[语音] {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[警告] 语音播放失败: {e}")


def find_on_screen(img_path, config):
    """
    在屏幕上查找模板图片中心点。
    返回 (x, y) 或 None。
    """
    try:
        pos = pyautogui.locateCenterOnScreen(
            img_path,
            confidence=config["confidence"],
            region=config["screen_region"],
        )
        return pos
    except pyautogui.ImageNotFoundException:
        return None
    except Exception as e:
        print(f"[错误] 查找 {img_path} 时异常: {e}")
        return None


def ensure_window_active():
    """简单等待，让 QQ 聊天窗口完成打开动画"""
    time.sleep(2)


def close_chat_window():
    """关闭当前聊天窗口"""
    pyautogui.keyDown("ctrl")
    pyautogui.keyDown("w")
    pyautogui.keyUp("w")
    pyautogui.keyUp("ctrl")


def type_reply(text):
    """清空输入框并输入回复"""
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")
    pyautogui.typewrite(text, interval=0.01)


def send_message(send_btn_pos, speaker, config):
    """点击发送按钮或按回车发送"""
    if send_btn_pos:
        speak(speaker, "发送消息")
        pyautogui.moveTo(send_btn_pos, duration=0.2)
        pyautogui.click()
    else:
        pyautogui.press("enter")
        speak(speaker, "消息已发送")


def process_new_message(speaker, config):
    """处理一条新消息：打开窗口、输入回复、发送、关闭"""
    # 1. 检测 QQ 消息图标
    qq_icon = find_on_screen(config["qq_icon"], config)
    if not qq_icon:
        return False

    speak(speaker, "有新的消息")

    # 2. 点击图标打开聊天窗口
    time.sleep(0.5)
    pyautogui.moveTo(qq_icon, duration=config["click_delay"])
    pyautogui.click()

    # 3. 等待窗口打开
    ensure_window_active()

    # 4. 查找输入框和发送按钮
    input_area = find_on_screen(config["input_area"], config)
    send_btn = find_on_screen(config["send_btn"], config)

    if not input_area:
        speak(speaker, "未找到输入框，跳过")
        close_chat_window()
        return True

    speak(speaker, "找到输入框")

    # 5. 输入自动回复
    pyautogui.moveTo(input_area, duration=config["click_delay"])
    pyautogui.click()
    type_reply(config["auto_reply"])

    # 6. 发送
    time.sleep(0.5)
    send_message(send_btn, speaker, config)

    # 7. 关闭窗口
    time.sleep(1)
    close_chat_window()
    return True


# ===================== 主程序 =====================
def main():
    print("=== QQ 自动回复脚本 ===")
    print("按 Ctrl+C 或把鼠标移到屏幕左上角可停止")
    print(f"自动回复内容: {CONFIG['auto_reply']}")

    speaker = init_speaker()
    speak(speaker, "QQ自动回复已启动")

    try:
        while True:
            processed = process_new_message(speaker, CONFIG)
            if not processed:
                time.sleep(CONFIG["check_interval"])
    except KeyboardInterrupt:
        print("\n[信息] 用户中断，正在停止...")
        speak(speaker, "已停止")
    except Exception as e:
        print(f"\n[错误] 脚本异常: {e}")
        speak(speaker, "脚本发生错误")


if __name__ == "__main__":
    main()
