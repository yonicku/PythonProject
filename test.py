import tkinter as tk
import threading
import queue
import keyboard
import time
import pygetwindow as gw
import pyautogui


# 메시지 큐 생성 (키 입력 명령 전달)
command_queue = queue.Queue()

# 현재 실행 중인 스레드와 상태를 관리
current_thread = None  # 현재 실행 중인 동작 스레드
current_action = None  # 현재 실행 중인 동작 이름
stop_event = threading.Event()  # 동작 중지를 위한 이벤트

# 키 입력 상태를 추적 (키가 처리 중인지 여부)
key_states = {"f2": False, "f3": False, "f4": False, "f5": False}

window = gw.getWindowsWithTitle("MapleStory Worlds-바람의나라 클래식")[0]
region = (window.left, window.top, window.width, window.height)

# 동작 정의 함수들
def mouse_right_click():
    """
    특정 영역에서 이미지 탐색 후 마우스 우클릭 수행.
    """
    if stop_event.is_set():
        return  # 중단 신호가 설정되면 종료

    start = time.time()  # 시작 시간 저장

    try:
        for img_file in ['image1.png', 'image2.png', 'image3.png', 'image4.png']:
            # 이미지 탐색
            location = pyautogui.locateCenterOnScreen(f'resource/image/{img_file}', region=region, confidence=0.3)
            if location:
                print(f"이미지 '{img_file}' 찾음: {location}")

                # 절대 좌표 계산
                absolute_location = (location[0], location[1])
                pyautogui.click(absolute_location, button="right")
            else:
                print(f"이미지 '{img_file}' 찾지 못함")
                pyautogui.rightClick()
    except Exception as e:
        print(f"mouse_right_click 실행 중 오류 발생: {e}")
        pyautogui.rightClick()

def keyboard_input(command):
    if stop_event.is_set():
        raise InterruptedError
    keyboard.send(command)

def f2_action():
    update_status("F2 동작 실행 중...")
    try:
        repeat_count_1 = 2  # 루프 반복 횟수 (기본값: 5)
        repeat_count_2 = 4  # 루프 반복 횟수 (기본값: 5)

        while True:  # 동작 반복 시작
            # 1. ESC 키 입력
            keyboard_input('esc')
            mouse_right_click()
            keyboard_input('2')
            keyboard_input('2')
            time.sleep(0.01)
            keyboard_input('1')
            for _ in range(repeat_count_1):
                mouse_right_click()
                keyboard_input('4')
                keyboard_input('up')
                time.sleep(0.01)
                keyboard_input('enter')
                mouse_right_click()
                keyboard_input('tab')
                time.sleep(0.01)
                keyboard_input('tab')
                for _ in range(repeat_count_2):
                    mouse_right_click()
                    keyboard_input('3')
                    time.sleep(0.03)
                keyboard_input('esc')
            time.sleep(0.02)
    except InterruptedError:
        update_status("F2 동작이 중단되었습니다.")
        pyautogui.rightClick()  # 일반 우클릭

def f3_action():
    """
    F3 동작: 5초간 수행하며 매초 중지 신호를 확인.
    """
    update_status("F3 동작 실행 중...")
    for i in range(5):
        if stop_event.is_set():
            update_status("F3 동작이 중단되었습니다.")
            return
        print(f"F3 실행 중... ({i + 1}초)")
        stop_event.wait(1)
    update_status("F3 동작 완료!")

def f4_action():
    """
    F4 동작: 7초간 수행하며 매초 중지 신호를 확인.
    """
    update_status("F4 동작 실행 중...")
    for i in range(7):
        if stop_event.is_set():
            update_status("F4 동작이 중단되었습니다.")
            return
        print(f"F4 실행 중... ({i + 1}초)")
        stop_event.wait(1)
    update_status("F4 동작 완료!")

def keyboard_input(command):
    if stop_event.is_set():
        raise InterruptedError
    keyboard.send(command)

def mouse_input(click):
    if stop_event.is_set():
        raise InterruptedError
    pyautogui.rightClick()  # 마우스 우클릭

def update_status(message):
    """
    상태를 업데이트하고 GUI에 표시하는 함수.
    :param message: 상태 메시지
    """
    status_label.config(text=f"상태: {message}")
    print(message)

def start_action(action_name):
    """
    새로운 동작을 시작하거나 기존 동작을 중단 후 시작.
    :param action_name: 실행할 동작의 이름 ('f2', 'f3', 'f4')
    """
    global current_thread, current_action, stop_event

    # 기존 동작 중지
    stop_all_actions()

    # 새로운 동작 시작
    stop_event.clear()
    current_action = action_name

    if action_name == "f2":
        current_thread = threading.Thread(target=f2_action)
    elif action_name == "f3":
        current_thread = threading.Thread(target=f3_action)
    elif action_name == "f4":
        current_thread = threading.Thread(target=f4_action)

    current_thread.start()

def stop_all_actions():
    """
    현재 실행 중인 모든 동작을 중단.
    """
    global current_thread, stop_event, current_action

    if current_thread and current_thread.is_alive():
        stop_event.set()  # 중지 신호 설정
        current_thread.join()  # 스레드 종료 대기
        current_thread = None
        current_action = None
        update_status("없음")  # 상태 초기화

def key_listener():
    """
    키 입력을 감지하고 해당 동작을 실행하는 함수.
    - F2: 동작 1 실행
    - F3: 동작 2 실행
    - F4: 동작 3 실행
    - F5: 모든 동작 중지
    """
    while True:
        for key in key_states.keys():
            if keyboard.is_pressed(key):
                if not key_states[key]:  # 키가 아직 처리되지 않았으면
                    key_states[key] = True
                    if key == "f2":
                        start_action("f2")
                    elif key == "f3":
                        start_action("f3")
                    elif key == "f4":
                        start_action("f4")
                    elif key == "f5":
                        stop_all_actions()
            else:
                key_states[key] = False  # 키 상태를 초기화

def create_gui():
    """
    GUI 생성 및 실행.
    """
    global status_label

    root = tk.Tk()
    root.title("매크로 프로그램")
    root.geometry("300x300")

    # 상태 표시 라벨
    status_label = tk.Label(root, text="상태: 없음", fg="blue", font=("Arial", 12))
    status_label.pack(pady=10)

    # 각 키에 대한 설명 라벨
    tk.Label(root, text="F2: 동작 1 실행", font=("Arial", 10)).pack(pady=5)
    tk.Label(root, text="F3: 동작 2 실행", font=("Arial", 10)).pack(pady=5)
    tk.Label(root, text="F4: 동작 3 실행", font=("Arial", 10)).pack(pady=5)
    tk.Label(root, text="F5: 모든 동작 중지", font=("Arial", 10), fg="red").pack(pady=5)

    # 키 입력 감지 스레드 실행
    threading.Thread(target=key_listener, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    print("GUI 매크로 프로그램이 시작되었습니다.")
    create_gui()