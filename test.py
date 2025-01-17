import tkinter as tk
import threading
import queue
import keyboard
import time
import pygetwindow as gw
import pyautogui

# --- 상수 정의 ---
COMMAND_QUEUE = queue.Queue()
KEY_STATES = {"f2": False, "f3": False, "f4": False, "f5": False}
STOP_EVENT = threading.Event()
CURRENT_THREAD = None
CURRENT_ACTION = None
WINDOW_TITLE = "MapleStory Worlds-바람의나라 클래식"

# --- 유틸리티 함수 ---
def locate_window(title):
    try:
        window = gw.getWindowsWithTitle(title)[0]
        return window.left, window.top, window.width, window.height
    except IndexError:
        raise ValueError(f"'{title}' 창을 찾을 수 없습니다.")

REGION = locate_window(WINDOW_TITLE)
REGION2 = [440,200,1100,700]


# --- 동작 함수 ---
def mouse_right_click():
    """특정 영역에서 이미지 탐색 후 마우스 우클릭 수행."""
    if STOP_EVENT.is_set():
        return

    image_files = ['image1.png', 'image2.png', 'image3.png', 'image4.png']

    for img_file in image_files:
        try:
            location = pyautogui.locateCenterOnScreen(
                f'resource/image/{img_file}', region=REGION2, confidence=0.4
            )
            if location:
                print(f"이미지 '{img_file}' 찾음: {location}")
                pyautogui.click(location, button="right", clicks=3, interval=0.1)
                return  # 이미지를 찾으면 더 이상 반복하지 않고 종료
            else:
                print(f"이미지 '{img_file}' 찾지 못함")
        except Exception as e:
            print(f"오류 발생: {e}")
            pyautogui.click(button="right", clicks=3, interval=0.1)

def keyboard_input(command):
    """키보드 명령 실행."""
    if STOP_EVENT.is_set():
        raise InterruptedError
    keyboard.send(command)

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
            mouse_right_click()
    except InterruptedError:
        update_status("F2 동작이 중단되었습니다.")

def repeat_action(action_name, duration):
    """특정 동작을 지정된 시간 동안 실행."""
    update_status(f"{action_name} 동작 실행 중...")
    for i in range(duration):
        if STOP_EVENT.is_set():
            update_status(f"{action_name} 동작이 중단되었습니다.")
            return
        print(f"{action_name} 실행 중... ({i + 1}초)")
        STOP_EVENT.wait(1)
    update_status(f"{action_name} 동작 완료!")


def f3_action():
    repeat_action("F3", 5)


def f4_action():
    repeat_action("F4", 7)


# --- 상태 관리 ---
def update_status(message):
    """상태를 업데이트하고 GUI에 표시."""
    status_label.config(text=f"상태: {message}")
    print(message)


def start_action(action_name):
    """새로운 동작을 시작."""
    global CURRENT_THREAD, CURRENT_ACTION
    stop_all_actions()
    STOP_EVENT.clear()
    CURRENT_ACTION = action_name

    action_map = {
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
                    if key == "f2":
                        start_action("f2")
                    elif key == "f3":
                        start_action("f3")
                    elif key == "f4":
                        start_action("f4")
                    elif key == "f5":
                        stop_all_actions()
            else:
                KEY_STATES[key] = False


# --- GUI 생성 ---
def create_gui():
    """GUI 생성."""
    global status_label

    root = tk.Tk()
    root.title("매크로 프로그램")
    root.geometry("300x300")

    status_label = tk.Label(root, text="상태: 없음", fg="blue", font=("Arial", 12))
    status_label.pack(pady=10)

    tk.Label(root, text="F2: 동작 1 실행", font=("Arial", 10)).pack(pady=5)
    tk.Label(root, text="F3: 동작 2 실행", font=("Arial", 10)).pack(pady=5)
    tk.Label(root, text="F4: 동작 3 실행", font=("Arial", 10)).pack(pady=5)
    tk.Label(root, text="F5: 모든 동작 중지", font=("Arial", 10), fg="red").pack(pady=5)

    threading.Thread(target=key_listener, daemon=True).start()

    root.mainloop()


if __name__ == "__main__":
    print("GUI 매크로 프로그램이 시작되었습니다.")
    create_gui()
