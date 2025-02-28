import cv2
import numpy as np
import pyautogui
import time
import threading
import tkinter as tk
import os

def get_resource_path(relative_path: str) -> str:
    """
    실행 파일이 있는 디렉토리를 기준으로 리소스 경로를 반환합니다.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class ImageDetector:
    """
    이미지 검색 관련 기능을 담은 클래스입니다.
    """

    def __init__(self, image_path: str, region: tuple[int, int, int, int], threshold: float = 0.5):
        """
        :param image_path: 검색할 이미지 경로
        :param region: (x, y, width, height) 형태로 스크린샷을 캡처할 영역
        :param threshold: 템플릿 매칭 시 유사도 임계값
        """
        self.image_path = image_path
        self.region = region
        self.threshold = threshold

        # 이미지 로드
        self.template = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
        if self.template is None:
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {self.image_path}")

        # 템플릿이 RGBA(4채널)면 BGR(3채널)로 변환
        if self.template.shape[-1] == 4:
            self.template = cv2.cvtColor(self.template, cv2.COLOR_BGRA2BGR)

        # 타입이 맞지 않으면 uint8로 변환
        if self.template.dtype != np.uint8:
            self.template = self.template.astype(np.uint8)

        # 템플릿 크기 (매칭 시 박스 표기를 위해 필요)
        self.template_h, self.template_w = self.template.shape[:2]

    def find(self) -> bool:
        """
        지정된 region에서 스크린샷을 찍은 뒤, 템플릿 매칭으로 해당 이미지를 찾습니다.
        찾으면 True, 찾지 못하면 False를 반환합니다.
        """
        screenshot = pyautogui.screenshot(region=self.region)
        screen_np = np.array(screenshot)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # 템플릿 매칭
        result = cv2.matchTemplate(screen_bgr, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # 항상 유사도 출력
        print(f"[{os.path.basename(self.image_path)}] similarity: {max_val:.4f}")

        if max_val >= self.threshold:
            return True
        else:
            # 매칭 실패 시 원하는 동작 (예: 창 닫기 또는 무시)
            # cv2.destroyWindow(f"Match - {os.path.basename(self.image_path)}")  # 필요하다면 창을 닫을 수도 있음
            return False


class CooldownApp:
    """
    Tkinter GUI를 통해 쿨타임을 표시하면서
    이미지를 검색하고, 조건에 따라 쿨타임을 시작하는 기능을 수행하는 클래스입니다.
    """

    def __init__(self, root: tk.Tk, detectors: list[ImageDetector], cooldown_time: float = 9.0):
        """
        :param root: Tkinter 메인 윈도우
        :param detectors: ImageDetector 객체 리스트
        :param cooldown_time: 쿨타임(초, 실수 가능)
        """
        self.root = root
        self.detectors = detectors
        self.cooldown_time = float(cooldown_time)

        # 쿨타임 상태 변수
        self.cooldown_active = False
        self.remaining_time = 0.0

        # Tkinter 위젯 구성
        self.root.title("쿨타임 표시")
        self.root.attributes("-topmost", True)
        self.root.geometry("200x50")

        self.label = tk.Label(self.root, text="이미지 감지 중...", font=("Arial", 14))
        self.label.pack()

        # UI 업데이트
        self.update_ui()

        # 이미지 감지를 위한 쓰레드 시작
        self.search_thread = threading.Thread(target=self.search_loop, daemon=True)
        self.search_thread.start()

    def search_loop(self):
        """
        주기적으로 이미지를 검색하고, 모든 Detector가 조건을 만족할 때 쿨타임을 시작합니다.
        """
        while True:
            if not self.cooldown_active:
                # 모든 ImageDetector가 이미지를 찾으면 True
                all_found = all(detector.find() for detector in self.detectors)
                if all_found:
                    print("모든 조건 충족! 쿨타임 시작...")
                    cooldown_thread = threading.Thread(target=self.cooldown_timer, daemon=True)
                    cooldown_thread.start()
            time.sleep(0.5)

    def cooldown_timer(self):
        """
        실제 시간을 기반으로 쿨타임을 더욱 정확하게 감소시키면서
        UI에 소수점 첫째 자리까지 표시합니다.
        """
        self.cooldown_active = True
        start_time = time.time()
        end_time = start_time + self.cooldown_time

        while True:
            now = time.time()
            self.remaining_time = end_time - now
            if self.remaining_time <= 0:
                self.remaining_time = 0
                break
            time.sleep(0.05)  # 또는 0.1

        self.cooldown_active = False

    def update_ui(self):
        """
        주기적으로 UI 라벨을 갱신하는 함수입니다.
        """
        if self.cooldown_active:
            # 소수점 이하 한 자리까지 표시
            self.label.config(text=f"헬 쿨타임: {self.remaining_time:.1f}초 남음")
        else:
            self.label.config(text="이미지 감지 중...")

        self.root.after(100, self.update_ui)


def main():
    """
    메인 함수. Tkinter 앱 초기화와 ImageDetector 설정을 여기서 진행합니다.
    """
    # 리소스 경로 지정 (테스트를 위해 임의 예시)
    TARGET_IMAGE_1 = get_resource_path("image/hell.png")
    TARGET_IMAGE_2 = get_resource_path("image/mana.png")

    # 검색 영역 설정 (x, y, width, height)
    SEARCH_REGION_1 = (1235, 685, 400, 150)
    SEARCH_REGION_2 = (1345, 930, 305, 30)

    # ImageDetector 생성
    detector1 = ImageDetector(image_path=TARGET_IMAGE_1, region=SEARCH_REGION_1, threshold=0.47)
    detector2 = ImageDetector(image_path=TARGET_IMAGE_2, region=SEARCH_REGION_2, threshold=0.5)

    # Tkinter 메인 윈도우
    root = tk.Tk()

    # CooldownApp 초기화 (쿨타임을 float으로 지정)
    app = CooldownApp(root=root, detectors=[detector1, detector2], cooldown_time=9.0)

    # Tkinter 이벤트 루프 실행
    root.mainloop()


if __name__ == "__main__":
    main()

'''import cv2
import numpy as np
import pyautogui
import time
import threading
import tkinter as tk
import os


def get_resource_path(relative_path: str) -> str:
    """
    실행 파일이 있는 디렉토리를 기준으로 리소스 경로를 반환합니다.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class ImageDetector:
    """
    이미지 검색 관련 기능을 담은 클래스입니다.
    """

    def __init__(self, image_path: str, region: tuple[int, int, int, int], threshold: float = 0.5):
        """
        :param image_path: 검색할 이미지 경로
        :param region: (x, y, width, height) 형태로 스크린샷을 캡처할 영역
        :param threshold: 템플릿 매칭 시 유사도 임계값
        """
        self.image_path = image_path
        self.region = region
        self.threshold = threshold

        # 이미지 로드 (필요 시, 첫 실행 시점에 로드하도록 변경 가능)
        self.template = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
        if self.template is None:
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {self.image_path}")

        # 템플릿이 RGBA(4채널)면 BGR(3채널)로 변환
        if self.template.shape[-1] == 4:
            self.template = cv2.cvtColor(self.template, cv2.COLOR_BGRA2BGR)

        # 타입이 맞지 않으면 uint8로 변환
        if self.template.dtype != np.uint8:
            self.template = self.template.astype(np.uint8)

    def find(self) -> bool:
        """
        지정된 region에서 스크린샷을 찍은 뒤, 템플릿 매칭으로 해당 이미지를 찾습니다.
        찾으면 True, 찾지 못하면 False를 반환합니다.
        """
        screenshot = pyautogui.screenshot(region=self.region)
        screen_np = np.array(screenshot)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # 템플릿 매칭
        result = cv2.matchTemplate(screen_bgr, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        return max_val >= self.threshold


class CooldownApp:
    """
    Tkinter GUI를 통해 쿨타임을 표시하면서
    이미지를 검색하고, 조건에 따라 쿨타임을 시작하는 기능을 수행하는 클래스입니다.
    """

    def __init__(self, root: tk.Tk, detectors: list[ImageDetector], cooldown_time: float = 8.5):
        """
        :param root: Tkinter 메인 윈도우
        :param detectors: ImageDetector 객체 리스트
        :param cooldown_time: 쿨타임(초)
        """
        self.root = root
        self.detectors = detectors
        self.cooldown_time = cooldown_time

        # 쿨타임 상태 변수
        self.cooldown_active = False
        self.remaining_time = 0

        # Tkinter 위젯 구성
        self.root.title("쿨타임 표시")
        self.root.attributes("-topmost", True)
        self.root.geometry("200x50")

        self.label = tk.Label(self.root, text="이미지 감지 중...", font=("Arial", 14))
        self.label.pack()

        # UI 업데이트
        self.update_ui()

        # 이미지 감지를 위한 쓰레드 시작
        self.search_thread = threading.Thread(target=self.search_loop, daemon=True)
        self.search_thread.start()

    def search_loop(self):
        """
        주기적으로 이미지를 검색하고, 모든 Detector가 조건을 만족할 때 쿨타임을 시작합니다.
        """
        while True:
            if not self.cooldown_active:
                # 모든 ImageDetector가 이미지를 찾으면 True
                all_found = all(detector.find() for detector in self.detectors)
                if all_found:
                    print("모든 조건 충족! 쿨타임 시작...")
                    cooldown_thread = threading.Thread(target=self.cooldown_timer, daemon=True)
                    cooldown_thread.start()

            time.sleep(0.5)

    def cooldown_timer(self):
        """
        쿨타임을 실제로 진행하고, 쿨타임이 끝나면 다시 이미지 검색 상태로 전환합니다.
        """
        self.cooldown_active = True
        self.remaining_time = self.cooldown_time

        while self.remaining_time > 0:
            time.sleep(1)
            self.remaining_time -= 1

        self.cooldown_active = False

    def update_ui(self):
        """
        주기적으로 UI 라벨을 갱신하는 함수입니다.
        """
        if self.cooldown_active:
            self.label.config(text=f"쿨타임: {self.remaining_time}초 남음")
        else:
            self.label.config(text="이미지 감지 중...")

        self.root.after(100, self.update_ui)


def main():
    """
    메인 함수. Tkinter 앱 초기화와 ImageDetector 설정을 여기서 진행합니다.
    """
    # 리소스 경로 지정
    TARGET_IMAGE_1 = get_resource_path("image/hell.png")
    TARGET_IMAGE_2 = get_resource_path("image/mana.png")

    # 검색 영역 설정 (x, y, width, height)
    SEARCH_REGION_1 = (1235, 685, 400, 150)
    SEARCH_REGION_2 = (1345, 930, 305, 30)

    # ImageDetector 생성
    detector1 = ImageDetector(image_path=TARGET_IMAGE_1, region=SEARCH_REGION_1, threshold=0.5)
    detector2 = ImageDetector(image_path=TARGET_IMAGE_2, region=SEARCH_REGION_2, threshold=0.5)

    # Tkinter 메인 윈도우
    root = tk.Tk()

    # CooldownApp 초기화
    app = CooldownApp(root=root, detectors=[detector1, detector2], cooldown_time=8.5)

    # Tkinter 이벤트 루프 실행
    root.mainloop()


if __name__ == "__main__":
    main()

import cv2
import numpy as np
import pyautogui
import time
import threading
import tkinter as tk
import os


# 실행 파일이 있는 디렉토리를 기준으로 리소스 경로 설정
def get_resource_path(relative_path):
    """ 실행 파일과 같은 디렉토리에 있는 리소스 경로를 반환 """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# 대상 이미지 파일 (외부 경로 유지)
TARGET_IMAGE_1 = get_resource_path("resource/image/hell.png")
TARGET_IMAGE_2 = get_resource_path("resource/image/hell2.png")  # 추가된 조건 이미지
COOLDOWN_TIME = 9  # 쿨타임 (초)

# 이미지 검색 영역 (x, y, width, height) 지정
SEARCH_REGION_1 = (1235, 685, 400, 150)  # TARGET_IMAGE_1 검색 영역
SEARCH_REGION_2 = (1345, 930, 305, 30)  # TARGET_IMAGE_2 검색 영역

# 쿨타임 변수 초기화
cooldown_active = False
remaining_time = 0


def find_image(target, region):
    """스크린에서 특정 이미지를 지정된 영역 내에서 찾음"""
    screenshot = pyautogui.screenshot(region=region)
    screen = np.array(screenshot)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)  # RGB -> BGR 변환

    template = cv2.imread(target, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"오류: 이미지 파일을 찾을 수 없음 -> {target}")
        return False, None

    # 템플릿 이미지가 4채널 (RGBA)라면 3채널로 변환
    if template.shape[-1] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    # 데이터 타입 확인 후 변환
    if template.dtype != np.uint8:
        template = template.astype(np.uint8)
    if screen.dtype != np.uint8:
        screen = screen.astype(np.uint8)

    # 템플릿 매칭 실행
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    threshold = 0.5  # 유사도 임계값
    if max_val >= threshold:
        return True, max_loc
    return False, None


def cooldown_timer():
    """쿨타임을 관리하는 함수"""
    global cooldown_active, remaining_time
    cooldown_active = True
    remaining_time = COOLDOWN_TIME

    while remaining_time > 0:
        time.sleep(1)
        remaining_time -= 1

    cooldown_active = False


def update_ui():
    """쿨타임 UI를 업데이트"""
    if cooldown_active:
        label.config(text=f"쿨타임: {remaining_time}초 남음")
    else:
        label.config(text="이미지 감지 중...")
    root.after(100, update_ui)


def search_loop():
    """이미지를 감지하고, 두 개의 조건을 만족하면 쿨타임을 실행하는 루프"""
    global cooldown_active
    while True:
        if not cooldown_active:
            found_1, _ = find_image(TARGET_IMAGE_1, SEARCH_REGION_1)
            found_2, _ = find_image(TARGET_IMAGE_2, SEARCH_REGION_2)

            if found_1 and found_2:  # 두 조건을 모두 만족해야 함
                print("두 개의 조건이 충족됨! 쿨타임 시작...")
                cooldown_thread = threading.Thread(target=cooldown_timer)
                cooldown_thread.start()
        time.sleep(0.5)


# UI 생성 (메인 스레드에서 실행)
root = tk.Tk()
root.title("쿨타임 표시")
root.attributes('-topmost', True)  # 항상 위에 표시
root.geometry("200x50")
label = tk.Label(root, text="이미지 감지 중...", font=("Arial", 14))
label.pack()
update_ui()

# 이미지 감지를 위한 쓰레드 실행
search_thread = threading.Thread(target=search_loop, daemon=True)
search_thread.start()

# UI 루프 실행 (메인 스레드)
root.mainloop()'''
