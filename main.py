import tkinter as tk
import keyboard
import threading
import time
import pygetwindow as gw
import pyautogui

# 전역 변수로 동작 상태 추적
"""f1_action_active = False
f2_action_active = False

def activate_window():

    windows = gw.getWindowsWithTitle("MapleStory Worlds-바람의나라 클래식")
    if not windows:
        raise Exception("Window with title not found.")
    window = windows[0]
    window.activate()
    return window

def perform_f1_action(window_title):

    while f1_action_active:
        try:
            activate_window(window_title)
            print("F1 동작 중")
            keyboard.send("ESC")
            time.sleep(0.2)
            keyboard.send("1")
            time.sleep(0.2)
            keyboard.send(",")
        except Exception as e:
            print(f"F1 동작 중 오류 발생: {e}")
            break

def perform_f2_action_start(window_title):

    global f1_action_active, f2_action_active

    if f2_action_active:
        return  # 이미 F2 동작 중인 경우 무시

    # 다른 동작 중지 후 F2 동작 시작
    f2_action_active = True
    print("F2 동작 시작")
    while f2_action_active:
        try:
            activate_window(window_title)
            keyboard.write("F2 Key Action\n")
            time.sleep(0.5)
        except Exception as e:
            print(f"F2 동작 중 오류 발생: {e}")
            break

def perform_f2_action_stop():

    global f2_action_active
    if f2_action_active:
        print("F2 동작 중지")
        f2_action_active = False

def key_listener(window_title):

    # F1 키 이벤트 등록
    keyboard.on_press_key('f1', lambda _: perform_f1_action(window_title))
    # F2 키 이벤트 등록
    keyboard.on_press_key('f2', lambda _: threading.Thread(target=perform_f2_action_start, args=(window_title,), daemon=True).start())
    keyboard.on_release_key('f2', lambda _: perform_f2_action_stop())

def start_key_listener(window_title):

    listener_thread = threading.Thread(target=key_listener, args=(window_title,))
    listener_thread.start()

def create_gui():

    root = tk.Tk()
    root.title("키 동작 제어")
    root.geometry("300x170")

    tk.Label(root, text="F1: 체력 회복 (토글)").pack(pady=5)
    tk.Label(root, text="F2: 혼 돌리기 (누르는 동안)").pack(pady=5)
    tk.Label(root, text="현재 상태: ").pack(pady=5)

    tk.Button(root, text="종료", command=root.destroy).pack()

    return root

# 메인 로직
if __name__ == "__main__":
    program_window_title = "MapleStory Worlds-바람의나라 클래식"
    start_key_listener(program_window_title)

    app = create_gui()
    app.mainloop()
"""
pyautogui.mouseInfo()