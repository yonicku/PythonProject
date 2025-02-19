import keyboard
import pyautogui
import time

def find_and_click_images(image_paths):

    for image_path in image_paths:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=0.8, region=(280,40,900,800))

            if location is not None:
                print(f"이미지가 화면에 표시되었습니다! ({image_path})")
                center = pyautogui.center(location)
                time.sleep(0.2)
                pyautogui.click(center)

        except Exception as e:
            print("왕 이미지 검색 중 오류 발생")
            continue  # 오류 발생 시 다음 이미지로 넘어감

    print("왕 이미지를 찾는 중...")
    time.sleep(0.2)

def find_and_press_key(image_paths, key_to_press):

    for image_path in image_paths:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=0.8, region=(280,40,900,800))

            if location is not None:
                print(f"이미지가 화면에 표시되었습니다! ({image_path})")
                pyautogui.press(key_to_press)  # 특정 키 누르기
                return  # 이미지 발견 후 루프 종료
        except Exception as e:
            print("팝업 이미지 검색 중 오류 발생")
            continue  # 오류 발생 시 다음 이미지로 넘어감





'''def popuphandler():
    while True:
        try:
            find_and_click_images(["resource/image/king1.png", "resource/image/king2.png"])
            if pyautogui.locateOnScreen("resource/image/down1.png", confidence=0.8, region=(280, 40, 900, 800)):
                time.sleep(0.2)
                pyautogui.press("down")
                time.sleep(0.2)
                pyautogui.press("space")
                print("미션1 확인 팝업")
            elif  pyautogui.locateOnScreen("resource/image/down2.png", confidence=0.8, region=(280, 40, 900, 800)):
                time.sleep(0.2)
                pyautogui.press("down")
                time.sleep(0.2)
                pyautogui.press("space")
                print("미션2 확인 팝업")
            elif pyautogui.locateOnScreen("resource/image/mong.png", confidence=0.8, region=(280, 40, 900, 800)) or pyautogui.locateOnScreen("resource/image/dok.png", confidence=0.8, region=(280, 40, 900, 800)):
                print("종료 조건 발견: mong 또는 dok")
                break
            else:  
                time.sleep(0.5)  # Add a delay to reduce CPU usage

        except pyautogui.ImageNotFoundException:
            # Handle cases where images are not found
            print("이미지를 찾을 수 없습니다. 기본 동작 실행  중...")
            pyautogui.press("space")
            time.sleep(0.5)  # Add a delay to avoid exc essive looping'''

# 무한 루프 실행
while True:
    popuphandler()