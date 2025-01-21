import tkinter as tk
import threading
import queue
import keyboard
import time
import pygetwindow as gw
import pyautogui
from PIL import ImageGrab
import cv2
import numpy as np

# --- 상수 정의 ---
COMMAND_QUEUE = queue.Queue()
KEY_STATES = {"f1": False, "f2": False, "f3": False, "f4": False}
STOP_EVENT = threading.Event()
CURRENT_THREAD = None
CURRENT_ACTION = None
WINDOW_TITLE = "MapleStory Worlds-바람의나라 클래식"
IMAGE_FILES = ['resource/image/up.png','resource/image/down.png','resource/image/left.png','resource/image/right.png']
TEMPLATES = {path: cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in IMAGE_FILES}
lock = threading.Lock()

# --- 유틸리티 함수 ---
def locate_window(title):
    try:
        window = gw.getWindowsWithTitle(title)[0]
        return window.left+190, window.top+31, 600, 550
    except IndexError:
        raise ValueError(f"'{title}' 창을 찾을 수 없습니다.")

# --- 동작 함수 ---
def match_template(screenshot_gray, template_path, x, y):
    template = TEMPLATES[template_path]
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    threshold = 0.8
    if STOP_EVENT.is_set():
        raise InterruptedError
    if max_val >= threshold:
        matched_location = max_loc
        screen_x = x + matched_location[0]
        screen_y = y + matched_location[1]
        print(f"Matched {template_path} at ({screen_x}, {screen_y}) with score {max_val}")
        pyautogui.moveTo(screen_x, screen_y)
        pyautogui.click(clicks=5, interval=0.1, button='right')
        return True
    return False

def move(region):
    x, y, w, h = region
    while not STOP_EVENT.is_set():
        # 스크린샷 캡처
        screenshot_pil = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        screenshot_np = np.array(screenshot_pil)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

        # 템플릿 매칭
        for template_path in TEMPLATES:
            if match_template(screenshot_gray, template_path, x, y):
                print("Template matched")
                return  # 매칭 성공 시 함수 종료

def keyboard_input(command):
    """키보드 명령 실행."""
    if STOP_EVENT.is_set():
        raise InterruptedError
    keyboard.send(command)

def f1_action():
    """F1 키 동작."""
    try:
        while not STOP_EVENT.is_set():
            keyboard_input('esc')
            keyboard_input('tab')
            time.sleep(0.06)
            keyboard_input('tab')
            keyboard_input('2')
            time.sleep(0.02)
            move(REGION)
            keyboard_input('2')
            keyboard_input('3')
            time.sleep(0.02)
            move(REGION)
            keyboard_input('3')
            time.sleep(0.02)
            move(REGION)
            keyboard_input('3')
            time.sleep(0.02)
            move(REGION)
            keyboard_input('3')
            time.sleep(0.02)
            move(REGION)
    except InterruptedError:
        update_status("F1 동작이 중단되었습니다.")

def f2_action():
    """F2 키 동작."""
    update_status("F2 동작 실행 중...")
    repeat_count_1 = 2
    repeat_count_2 = 5
    try:
        while not STOP_EVENT.is_set():
            keyboard_input('esc')
            keyboard_input('2')
            time.sleep(0.02)
            keyboard_input('2')
            time.sleep(0.02)
            keyboard_input('3')
            time.sleep(0.02)
            keyboard_input('home')
            time.sleep(0.02)
            keyboard_input('enter')
            keyboard_input('1')
            time.sleep(0.02)
            for _ in range(repeat_count_1):
                keyboard_input('4')
                time.sleep(0.02)
                keyboard_input('up')
                time.sleep(0.02)
                keyboard_input('enter')
                time.sleep(0.02)
                keyboard_input('tab')
                time.sleep(0.06)
                keyboard_input('tab')
                for _ in range(repeat_count_2):
                    keyboard_input('3')
                    time.sleep(0.01)
                keyboard_input('esc')
    except InterruptedError:
        update_status("F2 동작이 중단되었습니다.")

def f3_action():
    """F3 키 동작.(미구현)"""
    try:
        while not STOP_EVENT.is_set():
             keyboard_input('esc')
    except InterruptedError:
        update_status("F3 동작이 중단되었습니다.")

def f4_action():
    """F4 키 동작."""
    try:
        while not STOP_EVENT.is_set():
             keyboard_input('esc')
    except InterruptedError:
        update_status("F4 동작이 중단되었습니다.")

# --- 상태 관리 ---
def update_status(message):
    """상태를 업데이트하고 GUI에 표시."""
    status_label.config(text=f"상태: {message}")
    print(message)

def start_action(action_name):
    """새로운 동작을 시작."""
    global CURRENT_THREAD, CURRENT_ACTION
    with lock:
        stop_all_actions()
        STOP_EVENT.clear()
        CURRENT_ACTION = action_name

        action_map = {
            "f1": f1_action,
            "f2": f2_action,
            "f3": f3_action,
            "f4": f4_action
        }

        if action_name in action_map:
            CURRENT_THREAD = threading.Thread(target=action_map[action_name])
            CURRENT_THREAD.start()


def stop_all_actions():
    """현재 실행 중인 모든 동작 중단."""
    global CURRENT_THREAD, CURRENT_ACTION

    if CURRENT_THREAD and CURRENT_THREAD.is_alive():
        STOP_EVENT.set()
        CURRENT_THREAD.join()
    CURRENT_THREAD = None
    CURRENT_ACTION = None
    update_status("없음")


# --- 키 리스너 ---
def key_listener():
    """키 입력 감지 및 동작 실행."""
    while True:
        for key in KEY_STATES.keys():
            if keyboard.is_pressed(key):
                if not KEY_STATES[key]:
                    KEY_STATES[key] = True
                    if key == "f1":
                        start_action("f1")
                    elif key == "f2":
                        start_action("f2")
                    elif key == "f3":
                        start_action("f3")
                    elif key == "f4":
                        stop_all_actions()
            else:
                KEY_STATES[key] = False
        time.sleep(0.01)  # 대기 시간 추가

# --- GUI 생성 ---
def create_gui():
    global status_label

    root = tk.Tk()
    root.title("매크로 프로그램")
    root.geometry("300x300")

    status_label = tk.Label(root, text="상태: 없음", fg="blue", font=("Arial", 12))
    status_label.pack(pady=10)

    actions = [("F1: 동작 1 실행", "blue"), ("F2: 동작 2 실행", "blue"),
               ("F3: 동작 3 실행", "blue"), ("F4: 모든 동작 중지", "red")]

    for text, color in actions:
        tk.Label(root, text=text, font=("Arial", 10), fg=color).pack(pady=5)

    threading.Thread(target=key_listener, daemon=True).start()

    root.mainloop()


if __name__ == "__main__":
    print("GUI 매크로 프로그램이 시작되었습니다.")
    REGION = locate_window(WINDOW_TITLE)
    create_gui()

