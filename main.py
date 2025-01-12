import pyautogui
import pygetwindow as gw


def find_window(window_title): #창 활성화 함수

    windows = gw.getWindowsWithTitle(window_title)
    print("hi")
    if not windows:
        raise Exception(f"Window with title '{window_title}' not found.")
    window = windows[0]
    window.activate()
    time.sleep(0.5)
    return window

find_window("MapleStory Worlds-바람의나라 클래식")
