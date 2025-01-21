# --- 필요한 라이브러리 임포트 ---
import tkinter as tk  # GUI 생성 라이브러리
import threading  # 동시 실행을 위한 라이브러리
import queue  # 명령 처리를 위한 스레드 안전 큐
import keyboard  # 키보드 입력 감지를 위한 라이브러리
import time  # 시간 처리를 위한 유틸리티
import pygetwindow as gw  # 애플리케이션 창 위치를 가져오기 위한 라이브러리
import pyautogui  # 마우스 및 키보드 동작 자동화를 위한 라이브러리
from PIL import ImageGrab  # 스크린샷 캡처를 위한 라이브러리
import cv2  # 이미지 처리를 위한 OpenCV 라이브러리
import numpy as np  # 배열에 대한 수치 연산을 처리하기 위한 라이브러리

# --- 상수 ---
COMMAND_QUEUE = queue.Queue()  # 실행할 명령을 저장할 큐
KEY_STATES = {"f1": False, "f2": False, "f3": False, "f4": False}  # F1-F4 키의 현재 상태를 추적
STOP_EVENT = threading.Event()  # 스레드를 중단하기 위한 이벤트
CURRENT_THREAD = None  # 현재 실행 중인 스레드를 저장
CURRENT_ACTION = None  # 현재 실행 중인 동작 이름을 저장
WINDOW_TITLE = "MapleStory Worlds-바람의나라 클래식"  # 타겟 게임 창의 제목
IMAGE_FILES = ['resource/image/up.png','resource/image/down.png','resource/image/left.png','resource/image/right.png']  # 템플릿 이미지 경로
TEMPLATES = {path: cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in IMAGE_FILES}  # 템플릿 이미지를 그레이스케일로 로드
lock = threading.Lock()  # 스레드 동기화를 위한 락
status_label = None  # GUI 상태 라벨에 대한 참조

# --- 유틸리티 함수 ---
def locate_window(title):
    """창 제목으로 게임 창을 찾아 영역을 반환합니다."""
    try:
        window = gw.getWindowsWithTitle(title)[0]  # 제목에 해당하는 첫 번째 창 가져오기
        return window.left+190, window.top+31, 600, 550  # 게임 영역에 맞게 좌표 조정
    except IndexError:
        raise ValueError(f"'{title}' 창을 찾을 수 없습니다.")  # 창을 찾을 수 없을 때 오류 발생

# --- 동작 함수 ---
def match_template(screenshot_gray, template_path, x, y):
    """
    템플릿 이미지를 스크린샷에 매칭하고, 매칭되면 동작을 수행합니다.
    """
    template = TEMPLATES[template_path]  # 미리 로드된 템플릿 가져오기
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)  # 템플릿 매칭 수행
    _, max_val, _, max_loc = cv2.minMaxLoc(result)  # 최대 매칭 점수와 위치 가져오기
    threshold = 0.8  # 매칭을 인정할 최소 점수
    if STOP_EVENT.is_set():  # 정지 이벤트가 설정되었는지 확인
        raise InterruptedError  # 중단 신호가 있으면 동작 중단
    if max_val >= threshold:  # 매칭 점수가 임계값을 초과하면
        matched_location = max_loc
        screen_x = x + matched_location[0]  # 화면의 실제 x 좌표 계산
        screen_y = y + matched_location[1]  # 화면의 실제 y 좌표 계산
        print(f"Matched {template_path} at ({screen_x}, {screen_y}) with score {max_val}")
        pyautogui.moveTo(screen_x, screen_y)  # 매칭된 위치로 마우스 이동
        pyautogui.click(clicks=4, interval=0.1, button='right')  # 오른쪽 클릭 동작 실행
        return True  # 매칭 성공 반환
    return False  # 매칭 실패 반환

def move(region):
    """지정된 영역을 캡처하고 템플릿 매칭을 수행합니다."""
    x, y, w, h = region
    while not STOP_EVENT.is_set():  # 정지 이벤트가 설정될 때까지 반복
        screenshot_pil = ImageGrab.grab(bbox=(x, y, x+w, y+h))  # 영역의 스크린샷 캡처
        screenshot_np = np.array(screenshot_pil)  # NumPy 배열로 변환
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)  # 그레이스케일로 변환
        for template_path in TEMPLATES:  # 모든 템플릿 확인
            if match_template(screenshot_gray, template_path, x, y):  # 매칭이 성공하면
                print("Template matched")
                return  # 매칭 성공 후 종료

def keyboard_input(command):
    """키보드 명령을 전송합니다."""
    if STOP_EVENT.is_set():  # 정지 이벤트가 설정되었는지 확인
        raise InterruptedError
    keyboard.send(command)  # 키보드 입력 전송

def f1_action():
    """F1 키 동작을 수행합니다."""
    try:
        while not STOP_EVENT.is_set():
            keyboard_input('esc')  # 메뉴 닫기
            time.sleep(0.02)
            keyboard_input('tab')  # 다음 메뉴 또는 옵션으로 이동
            time.sleep(0.08)
            keyboard_input('tab')  # 다음 메뉴 또는 옵션으로 이동
            move(CHARREGION)  # 템플릿 기반 이동 수행
            keyboard_input('3')  # 미리 정의된 동작 실행
            time.sleep(0.1)
            keyboard_input('3')  # 미리 정의된 동작 실행
            time.sleep(0.1)
            keyboard_input('3')  # 미리 정의된 동작 실행
            time.sleep(0.1)
            keyboard_input('3')  # 미리 정의된 동작 실행
            time.sleep(0.1)
            move(CHARREGION)  # 템플릿 기반 이동 수행
    except InterruptedError:
        update_status("F1 동작이 중단되었습니다.")  # 중단 시 상태 업데이트
        
def f2_action():
    """F2 키 동작을 수행합니다."""
    try:
        while not STOP_EVENT.is_set():
            keyboard_input('esc')  # 메뉴 닫기
            time.sleep(0.02)
            keyboard_input('tab')  # 다음 메뉴 또는 옵션으로 이동
            time.sleep(0.08)
            move(CHARREGION)  # 템플릿 기반 이동 수행
            keyboard_input('3')  # 미리 정의된 동작 실행
            time.sleep(0.1)
    except InterruptedError:
        update_status("F2 동작이 중단되었습니다.")  # 중단 시 상태 업데이트

def f3_action():
    """F2 키 동작을 수행합니다."""
    try:
        while not STOP_EVENT.is_set():
            keyboard_input('esc')  # 메뉴 닫기
            time.sleep(0.02)
            keyboard_input('tab')  # 다음 메뉴 또는 옵션으로 이동
            time.sleep(0.08)
            move(CHARREGION)  # 템플릿 기반 이동 수행
            keyboard_input('3')  # 미리 정의된 동작 실행
            time.sleep(0.1)
    except InterruptedError:
        update_status("F3 동작이 중단되었습니다.")  # 중단 시 상태 업데이트

def f4_action():
    """F4 키 동작을 수행합니다."""
    stop_all_actions()
    update_status("없음")

# --- 상태 관리 ---
def update_status(message):
    """현재 상태를 업데이트하고 표시합니다."""
    status_label.config(text=f"상태: {message}")  # GUI 상태 라벨 업데이트
    print(message)  # 콘솔에 상태 출력

# --- 동작 시작/중지 ---
def start_action(action_name):
    """새 동작을 이름으로 시작합니다."""
    global CURRENT_THREAD, CURRENT_ACTION
    with lock:
        stop_all_actions()  # 실행 중인 모든 동작 중지
        STOP_EVENT.clear()  # 정지 이벤트 해제
        CURRENT_ACTION = action_name  # 현재 동작 이름 설정
        action_map = {
            "f1": f1_action,
            "f2": f2_action,
            "f3": f3_action,
            "f4": f4_action
        }
        if action_name in action_map:
            update_status(f"{action_name.upper()} 동작 실행 중")  # 상태 업데이트
            CURRENT_THREAD = threading.Thread(target=action_map[action_name])  # 동작을 실행할 스레드 생성
            CURRENT_THREAD.start()  # 스레드 시작

def stop_all_actions():
    """현재 실행 중인 모든 동작을 중지합니다."""
    global CURRENT_THREAD, CURRENT_ACTION
    if CURRENT_THREAD and CURRENT_THREAD.is_alive():  # 활성 스레드가 있는지 확인
        STOP_EVENT.set()  # 정지 신호 전송
        CURRENT_THREAD.join()  # 스레드가 종료될 때까지 대기
    CURRENT_THREAD = None  # 스레드 참조 초기화
    CURRENT_ACTION = None  # 동작 이름 초기화
    update_status("없음")  # 상태를 '없음'으로 업데이트

# --- 키 리스너 ---
def key_listener():
    """키 입력을 감지하고 동작을 실행합니다."""
    while True:
        for key in KEY_STATES.keys():
            if keyboard.is_pressed(key):  # 키가 눌렸는지 확인
                if not KEY_STATES[key]:  # 이전에 눌리지 않았다면
                    KEY_STATES[key] = True
                    if key == "f1":
                        start_action("f1")  # F1 동작 시작
                    elif key == "f2":
                        start_action("f2")  # F2 동작 시작
                    elif key == "f3":
                        start_action("f3")  # F3 동작 시작
                    elif key == "f4":
                        stop_all_actions()  # 모든 동작 중지
            else:
                KEY_STATES[key] = False  # 키 상태 초기화
        time.sleep(0.01)  # 과도한 CPU 사용 방지를 위해 대기 시간 추가

# --- GUI 생성 ---
def create_gui():
    """매크로 프로그램 GUI를 생성합니다."""
    global status_label
    root = tk.Tk()  # Tkinter 루트 창 초기화
    root.title("매크로 프로그램")  # 창 제목 설정
    root.geometry("300x300")  # 창 크기 설정

    status_label = tk.Label(root, text="상태: 없음", fg="blue", font=("Arial", 12))  # 상태 라벨 생성
    status_label.pack(pady=10)  # 패딩 추가 및 창에 배치

    actions = [("F1: 동작 1 실행", "blue"), ("F2: 동작 2 실행", "blue"),
               ("F3: 동작 3 실행", "blue"), ("F4: 모든 동작 중지", "red")]  # 동작 라벨 정의

    for text, color in actions:
        tk.Label(root, text=text, font=("Arial", 10), fg=color).pack(pady=5)  # 각 동작에 대한 라벨 생성

    threading.Thread(target=key_listener, daemon=True).start()  # 키 리스너 스레드 시작

    root.mainloop()  # Tkinter 메인 루프 시작

# --- 메인 실행 ---
if __name__ == "__main__":
    print("GUI 매크로 프로그램이 시작되었습니다.")  # 프로그램 시작 메시지 출력
    CHARREGION = locate_window(WINDOW_TITLE)  # 게임 창 위치 찾기
    create_gui()  # GUI 실행
