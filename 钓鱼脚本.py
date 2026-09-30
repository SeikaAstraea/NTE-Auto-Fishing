import cv2
import numpy as np
import time
import pydirectinput
from mss import mss
import os
import keyboard
# 假设 cv2, numpy, mss 的基础截屏功能已按之前讨论封装好
# from your_vision_module import capture_roi, check_bar_exist, check_idle_icon_exist, get_bar_positions
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

class FishingBot:
    def __init__(self):
        self.sct = mss()
        self.state = "IDLE"
        
        # === 全屏 1920x1080/1280 坐标配置 ===
        # 覆盖右下角较大区域，确保不同高度比例都能截到 F 图标
        self.monitor_icon = {"top": 700, "left": 1400, "width": 520, "height": 500}
        # 覆盖正上方较宽的区域，抓取进度条
        self.monitor_bar = {"top": 65, "left": 600, "width": 720, "height": 15}
        
        # 加载 F 按钮模板并进行二值化处理
        template = cv2.imread('template_f.png', cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError("找不到 template_f.png！请检查文件路径。")
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        _, self.thresh_template = cv2.threshold(gray_template, 200, 255, cv2.THRESH_BINARY)

    def get_screen(self, monitor):
        """截取指定区域"""
        img = np.array(self.sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def is_idle_icon_visible(self):
        """检测右下角抛竿图标"""
        frame = self.get_screen(self.monitor_icon)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh_frame = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)
        
        result = cv2.matchTemplate(thresh_frame, self.thresh_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return max_val > 0.8 

    def get_bar_positions(self):
        """获取绿条和黄条的中心坐标"""
        frame = self.get_screen(self.monitor_bar)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # HSV 颜色范围
        lower_cyan = np.array([70, 100, 100])
        upper_cyan = np.array([100, 255, 255])
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])

        mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        cyan_count = cv2.countNonZero(mask_cyan)
        yellow_count = cv2.countNonZero(mask_yellow)

        # 像素数量防误报
        if cyan_count > 100 and yellow_count > 30:
            cyan_x = int(np.mean(np.where(mask_cyan > 0)[1]))
            yellow_x = int(np.mean(np.where(mask_yellow > 0)[1]))
            return cyan_x, yellow_x
        return None, None

    def run(self):
        print("====== 自动化钓鱼脚本已启动 (全屏模式) ======")
        print("💡 提示: 随时按住键盘上的 【ESC】 键即可强制停止脚本！")
        print("等待进入钓鱼主界面...\n")
        
        try:
            while True:
                # 全局急停检测
                if keyboard.is_pressed('esc'):
                    print("\n[紧急停止] 检测到 ESC 键按下，脚本中止。")
                    break

                if self.state == "IDLE":
                    if self.is_idle_icon_visible():
                        print(f"[{time.strftime('%H:%M:%S')}] 🎣 [抛竿阶段] 发现抛竿图标，自动按 F！")
                        pydirectinput.press('f')
                        time.sleep(5)  # 等待 5 秒动画
                        self.state = "BLIND_HOOKING"
                
                elif self.state == "BLIND_HOOKING":
                    pydirectinput.press('f')
                    time.sleep(1) # 每秒盲按
                    
                    cyan_x, yellow_x = self.get_bar_positions()
                    if cyan_x is not None:
                        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ [状态切换] 进度条出现，鱼上钩，开始溜鱼！")
                        self.state = "FIGHTING"

                elif self.state == "FIGHTING":
                    cyan_x, yellow_x = self.get_bar_positions()
                    
                    if cyan_x is not None and yellow_x is not None:
                        tolerance = 25 # 容差设定为 25 像素
                        if yellow_x < cyan_x - tolerance:
                            pydirectinput.keyUp('a')
                            pydirectinput.keyDown('d')
                        elif yellow_x > cyan_x + tolerance:
                            pydirectinput.keyUp('d')
                            pydirectinput.keyDown('a')
                        else:
                            pydirectinput.keyUp('a')
                            pydirectinput.keyUp('d')
                        
                        time.sleep(0.05)
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] 🏁 [状态切换] 进度条消失，溜鱼结束，进入结算盲点。")
                        pydirectinput.keyUp('a')
                        pydirectinput.keyUp('d')
                        time.sleep(3) # 缓冲时间，等待结算UI完全弹出
                        self.state = "BLIND_SETTLEMENT"

                elif self.state == "BLIND_SETTLEMENT":
                    pydirectinput.click()
                    time.sleep(1.5)
                    
                    if self.is_idle_icon_visible():
                        print(f"[{time.strftime('%H:%M:%S')}] ✅ [循环完成] 成功回到主界面，准备下一次抛竿。\n")
                        self.state = "IDLE"
                        time.sleep(2) 

        except Exception as e:
            print(f"\n运行中发生错误: {e}")
        finally:
            # 无论是报错还是手动停止，都确保释放键盘，防止游戏人物一直往旁边跑
            pydirectinput.keyUp('a')
            pydirectinput.keyUp('d')
            print("🛑 脚本已安全退出，按键已完全释放。")

if __name__ == "__main__":
    bot = FishingBot()
    bot.run()