import cv2
import numpy as np
import os
from PIL import ImageGrab
import time

# 특정 영역에서 매칭 및 사각형 그리기 함수
def find_and_draw_matches_in_region(screenshot, template_images, region):
    x, y, w, h = region
    cropped_screenshot = screenshot[y:y+h, x:x+w]
    screenshot_gray = cv2.cvtColor(cropped_screenshot, cv2.COLOR_BGR2GRAY)

    for template_path in template_images:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"이미지를 로드할 수 없습니다: {template_path}")
            continue

        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        time.sleep(1.0)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.7  # 임계값 조정
        print(f"템플릿: {template_path}, 매칭 점수: {max_val}")
        if max_val >= threshold:
            h_t, w_t = template.shape[:2]
            top_left = (max_loc[0] + x, max_loc[1] + y)  # 전체 스크린샷 기준 좌표 변환
            bottom_right = (top_left[0] + w_t, top_left[1] + h_t)

            cv2.rectangle(screenshot, top_left, bottom_right, (0, 0, 255), 2)

            output_path = "matched_screenshot_in_region.png"
            cv2.imwrite(output_path, screenshot)
            print(f"매칭 발견! 스크린샷이 {output_path}로 저장되었습니다.")
            break

# 화면 모니터링 함수 (특정 영역)
def monitor_screen_in_region(folder_path, region):
    if not os.path.exists(folder_path):
        print(f"폴더 경로가 존재하지 않습니다: {folder_path}")
        return

    template_images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith((".png", ".jpg", ".jpeg"))]
    if not template_images:
        print("폴더에 템플릿 이미지가 없습니다.")
        return

    print("지정된 영역에서 매칭을 모니터링 중입니다...")
    while True:
        # 전체 화면 스크린샷 캡처
        screenshot_pil = ImageGrab.grab()
        screenshot_np = np.array(screenshot_pil)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        # 관심 영역 스크린샷 저장
        x, y, w, h = region
        cropped_screenshot = screenshot_bgr[y:y+h, x:x+w]
        region_screenshot_path = "region_screenshot.png"
        time.sleep(1)
        cv2.imwrite(region_screenshot_path, cropped_screenshot)
        print(f"관심 영역 스크린샷이 {region_screenshot_path}로 저장되었습니다.")

        find_and_draw_matches_in_region(screenshot_bgr, template_images, region)

# 예제 실행 코드
image_folder = r"resource\image"  # 실제 템플릿 이미지 폴더 경로 입력
region = (280,40,900,800)  # 관심 영역 정의 (x 좌표, y 좌표, 너비(width), 높이(height))

monitor_screen_in_region(image_folder, region)
