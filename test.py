import tkinter as tk
import threading
import time
import keyboard

# 스레드 종료를 제어하기 위한 이벤트 객체
stop_event = threading.Event()

# 현재 실행 중인 스레드와 상태
current_thread = None
current_action = None


# 키에 설정된 동작 정의
def f2_action():
    update_status("F2 동작 실행 중...")
    for i in range(10):  # 동작을 10초 동안 반복
        if stop_event.is_set():
            update_status("F2 동작이 중단되었습니다.")
            return
        time.sleep(1)
    update_status("F2 동작 완료!")


def f3_action():
    update_status("F3 동작 실행 중...")
    for i in range(5):  # 예시로 5초간 작업
        if stop_event.is_set():
            update_status("F3 동작이 중단되었습니다.")
            return
        time.sleep(1)
    update_status("F3 동작 완료!")


def f4_action():
    update_status("F4 동작 실행 중...")
    for i in range(7):  # 예시로 7초간 작업
        if stop_event.is_set():
            update_status("F4 동작이 중단되었습니다.")
            return
        time.sleep(1)
    update_status("F4 동작 완료!")


# 상태를 업데이트하는 함수
def update_status(message):
    status_label.config(text=f"상태: {message}")
    print(message)


# 동작을 시작하는 함수
def start_action(action_name):
    global current_thread, stop_event, current_action

    # 기존 동작 중지
    if current_thread and current_thread.is_alive():
        stop_all_actions()

    # 새로운 동작 시작
    stop_event.clear()  # 새로운 동작을 위해 이벤트 초기화
    current_action = action_name  # 현재 동작 업데이트
    if action_name == 'f2':
        current_thread = threading.Thread(target=f2_action)
    elif action_name == 'f3':
        current_thread = threading.Thread(target=f3_action)
    elif action_name == 'f4':
        current_thread = threading.Thread(target=f4_action)

    current_thread.start()


# 모든 동작을 중지하는 함수
def stop_all_actions():
    global current_thread, stop_event, current_action

    if current_thread and current_thread.is_alive():
        update_status("모든 동작을 중지합니다.")
        stop_event.set()  # 스레드 종료 신호 설정
        current_thread.join()  # 스레드 종료 대기
        current_thread = None  # 실행 중인 스레드 초기화
        current_action = None  # 현재 동작 초기화
        update_status("없음")


# 키 입력 감지 함수
def key_listener():
    while True:
        if keyboard.is_pressed('f2'):
            start_action('f2')
        elif keyboard.is_pressed('f3'):
            start_action('f3')
        elif keyboard.is_pressed('f4'):
            start_action('f4')
        elif keyboard.is_pressed('f5'):
            stop_all_actions()
        time.sleep(0.1)


# GUI 설정
def create_gui():
    global status_label

    # 메인 윈도우 설정
    root = tk.Tk()
    root.title("매크로 프로그램")
    root.geometry("300x300")

    # 상태 표시
    status_label = tk.Label(root, text="상태: 없음", fg="blue", font=("Arial", 12))
    status_label.pack(pady=10)

    # 설명 추가
    label_f2 = tk.Label(root, text="F2: 동작 1 실행", font=("Arial", 10))
    label_f2.pack(pady=5)

    label_f3 = tk.Label(root, text="F3: 동작 2 실행", font=("Arial", 10))
    label_f3.pack(pady=5)

    label_f4 = tk.Label(root, text="F4: 동작 3 실행", font=("Arial", 10))
    label_f4.pack(pady=5)

    label_f5 = tk.Label(root, text="F5: 모든 동작 중지", font=("Arial", 10), fg="red")
    label_f5.pack(pady=5)

    # 키 감지 스레드 시작
    threading.Thread(target=key_listener, daemon=True).start()

    # GUI 실행
    root.mainloop()


# 프로그램 실행
if __name__ == "__main__":
    print("GUI 매크로 프로그램이 시작되었습니다.")
    create_gui()
