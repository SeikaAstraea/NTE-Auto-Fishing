import cv2
import numpy as np
from mss import mss
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

def test_icon_detection():
    # 1. 读取你保存的模板图片
    # cv2.IMREAD_COLOR 表示以彩色模式读取
    template = cv2.imread('template_f.png', cv2.IMREAD_COLOR)
    
    if template is None:
        print("错误：找不到 template_f.png，请检查图片路径和名字！")
        return

    # 2. 定义屏幕截图的区域 (ROI)
    # 这里截取的是 1920x1080 屏幕的右下角 400x380 大小的区域
    # 缩小截图范围能大幅度提升程序运行速度
    monitor = {"top": 700, "left": 1500, "width": 400, "height": 380}
    
    sct = mss()
    print("开始盯着屏幕右下角... (按 Ctrl+C 停止运行)")

    while True:
        # 3. 截取游戏画面
        screenshot = sct.grab(monitor)
        
        # 将 mss 截下来的图片转换成 OpenCV 认识的格式 (BGRA 转 BGR)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # 4. 进行模板匹配！
        # TM_CCOEFF_NORMED 是一种非常常用的匹配算法，对光照变化有一定容忍度
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        
        # 获取匹配结果中的最大相似度和位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 5. 判断相似度是否达标
        # max_val 满分是 1.0，0.8 (80%) 是个不错的及格线
        if max_val > 0.8:
            print(f"[{time.strftime('%H:%M:%S')}] 🎣 发现抛竿图标！(相似度: {max_val:.2f})")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 没看到图标... (最高相似度仅为: {max_val:.2f})")

        # 休息 1 秒再看，防止刷屏太快
        time.sleep(1)

if __name__ == "__main__":
    test_icon_detection()
