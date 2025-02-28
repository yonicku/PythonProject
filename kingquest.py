import pyautogui
import keyboard
import time
import threading

# 마우스 클릭 기능을 수행하는 함수
def click_on_image(image_path, similarity=0.8, region=None):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=similarity, region=region)
    except Exception:
        location = None

    if location:
        #print(f"이미지 '{image_path}' 매칭됨. 위치: {location}. 클릭 수행.")
        pyautogui.click(location)

# 키 입력 기능을 수행하는 함수
def press_key_on_image(image_path, key='a', similarity=0.8, region=None):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=similarity, region=region)
    except Exception:
        location = None

    if location:
        #print(f"이미지 '{image_path}' 매칭됨. 위치: {location}. 키 '{key}' 입력 수행.")
        pyautogui.press(key)
        pyautogui.press('space')
        return True
    else:
        pyautogui.keyDown('space')
        time.sleep(0.2)
        pyautogui.keyUp('space')
        return False

# monster 함수: 이미지가 감지되면 매크로를 중지하고 True 반환
def monster(image_path, key='a', similarity=0.8, region=None):
    global macro_enabled
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=similarity, region=region)
    except Exception:
        location = None

    if location:
        if image_path == 'resource/image/dok.png':
            print(f'\033[95m'+'독충'+'\033[0m')
        else:
            print(f'\033[92m'+'몽달'+'\033[0m')
        pyautogui.press('esc')
        macro_enabled = False
        return True  # 이미지가 감지되었으므로 True 반환
    else:
        #print(f"이미지 '{image_path}' 매칭 실패.")
        return False

# 매크로 on/off 토글을 위한 플래그와 함수
macro_enabled = False

def toggle_macro():
    global macro_enabled
    macro_enabled = not macro_enabled
    state = "활성화" if macro_enabled else "비활성화"
    print(f"매크로 {state}됨.")

# 매크로 동작 루프를 별도 스레드로 실행
def macro_loop():
    while True:
        if macro_enabled:
            press_key_on_image("resource/image/down1.png", key='down', similarity=0.8, region=(560, 340, 140, 120))
            time.sleep(0.16)
            monster("resource/image/dok.png", similarity=0.7, region=(780, 270, 420, 390))
            time.sleep(0.01)
            monster("resource/image/mong.png", similarity=0.7, region=(780, 270, 420, 390))
            time.sleep(0.01)
            press_key_on_image("resource/image/down2.png", key='down', similarity=0.8, region=(590, 360, 80, 90))
            time.sleep(0.16)
            click_on_image("resource/image/king1.png", similarity=0.8, region=(270, 20, 910, 180))
            click_on_image("resource/image/king2.png", similarity=0.8, region=(270, 20, 910, 180))
        else:
            time.sleep(0.01)
            # 매크로 비활성 시 CPU 사용량을 낮추기 위한 슬립

if __name__ == '__main__':
    # 전역 단축키 등록: 백그라운드에서도 작동합니다.
    keyboard.add_hotkey('\\', toggle_macro)
    print("\\ 키를 눌러 매크로 활성/비활성을 전환합니다.")

    # 매크로 루프를 별도의 데몬 스레드로 시작
    t = threading.Thread(target=macro_loop)
    t.daemon = True
    t.start()

    # 메인 스레드는 키 입력을 계속 대기 (백그라운드에서도 단축키 수신 가능)
    keyboard.wait()  # 프로그램이 종료되지 않고 계속 실행됨\  
