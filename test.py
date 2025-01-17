import tkinter as tk
import threading
import queue
import keyboard

# 메시지 큐 생성
command_queue = queue.Queue()

# 현재 실행 중인 스레드와 실행 상태를 저장
current_thread = None
current_action = None
stop_event = threading.Event()  # 중지 신호 이벤트 객체

# 키 입력 상태를 추적
key_states = {"f2": False, "f3": False, "f4": False, "f5": False}

# 동작 정의 함수들
def f2_action():
    update_status("F2 동작 실행 중...")
    for i in range(10):
        if stop_event.is_set():
            update_status("F2 동작이 중단되었습니다.")
            return
        print(f"F2 실행 중... ({i + 1}초)")
        stop_event.wait(1)
    update_status("F2 동작 완료!")

def f3_action():
    update_status("F3 동작 실행 중...")
    for i in range(5):
        if stop_event.is_set():
            update_status("F3 동작이 중단되었습니다.")
            return
        print(f"F3 실행 중... ({i + 1}초)")
        stop_event.wait(1)
    update_status("F3 동작 완료!")

def f4_action():
    update_status("F4 동작 실행 중...")
    for i in range(7):
        if stop_event.is_set():
            update_status("F4 동작이 중단되었습니다.")
            return
        print(f"F4 실행 중... ({i + 1}초)")
        stop_event.wait(1)
    update_status("F4 동작 완료!")

def update_status(message):
    status_label.config(text=f"상태: {message}")
    print(message)

def start_action(action_name):
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
    global current_thread, stop_event, current_action

    if current_thread and current_thread.is_alive():
        stop_event.set()
        current_thread.join()
        current_thread = None
        current_action = None
        update_status("없음")

def key_listener():
    while True:
        for key in key_states.keys():
            if keyboard.is_pressed(key):
                if not key_states[key]:  # 키가 아직 처리되지 않았으면
                    key_states[key] = True  # 키 상태를 활성화
                    if key == "f2":
                        start_action("f2")
                    elif key == "f3":
                        start_action("f3")
                    elif key == "f4":
                        start_action("f4")
                    elif key == "f5":
                        stop_all_actions()
            else:
                key_states[key] = False  # 키 상태를 비활성화

def create_gui():
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
