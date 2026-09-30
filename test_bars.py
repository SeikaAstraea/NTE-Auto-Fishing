import cv2
import numpy as np
from mss import mss
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
def test_bar_detection():
    # 定义屏幕上方进度条的大致区域 (基于 1920x1080 估算)
    # 截取靠上方的、横跨中间的矩形
    monitor = {"top": 50, "left": 400, "width": 1100, "height": 150}
    sct = mss()
    print("开始检测上方进度条... (按 Ctrl+C 停止运行)")

    while True:
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # 1. 将图像转换到 HSV 色彩空间
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # 2. 定义青绿色（目标条）的 HSV 范围
        # 这里的数值可能需要根据你的实际游戏画面微调
        lower_cyan = np.array([70, 100, 100])
        upper_cyan = np.array([100, 255, 255])
        
        # 3. 定义黄色（当前张力）的 HSV 范围
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])

        # 4. 根据范围过滤颜色，生成黑白掩膜 (Mask)
        # 对应的颜色会变成白色，其他统统变成黑色
        mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # 5. 计算青绿色条的中心 X 坐标
        cyan_x = None
        # np.where 找出所有白色像素点的坐标 (y, x)
        y_c, x_c = np.where(mask_cyan > 0) 
        if len(x_c) > 0:
            cyan_x = int(np.mean(x_c)) # 取所有X坐标的平均值作为中心点

        # 6. 计算黄色条的中心 X 坐标
        yellow_x = None
        y_y, x_y = np.where(mask_yellow > 0)
        if len(x_y) > 0:
            yellow_x = int(np.mean(x_y))

        # 7. 打印结果
        if cyan_x is not None and yellow_x is not None:
            print(f"[{time.strftime('%H:%M:%S')}] 🎣 溜鱼中 | 绿条中心: {cyan_x} | 黄条位置: {yellow_x}")
            
            # 顺便输出一下控制逻辑的雏形
            if yellow_x < cyan_x - 15:
                print("   -> 偏左，需要按 D 往右拉")
            elif yellow_x > cyan_x + 15:
                print("   -> 偏右，需要按 A 往左拉")
            else:
                print("   -> 完美在区间内，保持！")
                
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 未检测到完整的进度条 (未在溜鱼状态)")

        # 稍微快一点刷新，方便你看动态效果
        time.sleep(0.1)

if __name__ == "__main__":
    test_bar_detection()
