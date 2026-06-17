import serial
import threading
import tkinter as tk
from tkinter import ttk

COM_PORT = 'COM3'  # 請修正為你實際的 COM 埠
BAUD_RATE = 115200

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
except Exception as e:
    print(f"無法連線到 {COM_PORT}，請檢查序列埠。")
    exit()

# 影音初始狀態
video_progress = 30  # 播放進度 %
audio_volume = 50    # 音量大小 %
ui_mode = "普通明亮模式"

def serial_listen():
    global video_progress, audio_volume, ui_mode
    
    # 建立兩個記憶變數，用來記錄按鈕的「上一次狀態」
    last_the_btn = "0"
    last_mut_btn = "0"
    
    while True:
        try:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line.startswith("X:"):
                    parts = line.split(",")
                    raw_x = int(parts[0].split(":")[1])
                    raw_y = int(parts[1].split(":")[1])
                    the_btn = parts[2].split(":")[1]
                    mut_btn = parts[3].split(":")[1]
                    
                    # 1. 搖桿左右推 (X軸)
                    if raw_x > 3200: video_progress = min(100, video_progress + 1)
                    elif raw_x < 800: video_progress = max(0, video_progress - 1)
                    
                    # 2. 搖桿上下推 (Y軸)
                    if raw_y < 800: audio_volume = min(100, audio_volume + 2)
                    elif raw_y > 3200: audio_volume = max(0, audio_volume - 2)
                    
                    # 3. 按鈕 1 ➔ 劇院雙向切換開關 (加入防連按機制)
                    # 只有在「上一次是0，這一次是1」的瞬間才執行！
                    if the_btn == "1" and last_the_btn == "0":
                        if "劇院模式" not in ui_mode:
                            ui_mode = "🍿 劇院模式開啟 (環境昏暗)"
                            root.after(0, lambda: change_theme("#111111", "#FFFFFF", "yellow"))
                            ser.write(b"LED_THEATER\n")
                        else:
                            ui_mode = "☀️ 系統復位 (全室明亮)"
                            root.after(0, lambda: change_theme("#F0F0F0", "#000000", "green"))
                            ser.write(b"LED_NORMAL\n")
                            
                    # 4. 按鈕 2 ➔ 靜音/復位鈕 (同樣加入防連按機制)
                    if mut_btn == "1" and last_mut_btn == "0":
                        ui_mode = "☀️ 系統復位 (全室明亮)"
                        audio_volume = 0
                        video_progress = 0
                        root.after(0, lambda: change_theme("#F0F0F0", "#000000", "green"))
                        ser.write(b"LED_NORMAL\n")
                    
                    # ★ 最重要的一步：在這一輪結束前，把現在的狀態記錄下來，變成下一次的「過去式」
                    last_the_btn = the_btn
                    last_mut_btn = mut_btn
                    
                    # 即時更新電腦畫面
                    root.after(0, update_display)
        except Exception as e:
            break
def change_theme(bg_color, fg_color, accent):
    root.config(bg=bg_color)
    lbl_title.config(bg=bg_color, fg=fg_color)
    lbl_mode.config(bg=bg_color, fg=accent)
    lbl_p.config(bg=bg_color, fg=fg_color)
    lbl_v.config(bg=bg_color, fg=fg_color)

def update_display():
    progress_bar['value'] = video_progress
    volume_bar['value'] = audio_volume
    lbl_p.config(text=f"🎬 影片播放進度: {video_progress} %")
    lbl_v.config(text=f"🔊 劇院環繞音量: {audio_volume} %")
    lbl_mode.config(text=f"🎬 目前情境: {ui_mode}")

# 建立 GUI 視窗
root = tk.Tk()
root.title("IoT 智能家庭劇院手勢中控台")
root.geometry("500x320")
root.config(bg="#F0F0F0")

lbl_title = tk.Label(root, text="🍿 智慧家居：影音手勢控制器", font=("Microsoft JhengHei", 16, "bold"), bg="#F0F0F0")
lbl_title.pack(pady=20)

lbl_mode = tk.Label(root, text="🎬 目前情境: ☀️ 系統復位 (全室明亮)", font=("Microsoft JhengHei", 12, "bold"), fg="green", bg="#F0F0F0")
lbl_mode.pack(pady=5)

# 進度條組件
lbl_p = tk.Label(root, text="🎬 影片播放進度: 30 %", font=("Microsoft JhengHei", 11), bg="#F0F0F0")
lbl_p.pack(pady=5)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=5)
progress_bar['value'] = video_progress

# 音量條組件
lbl_v = tk.Label(root, text="🔊 劇院環繞音量: 50 %", font=("Microsoft JhengHei", 11), bg="#F0F0F0")
lbl_v.pack(pady=5)
volume_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
volume_bar.pack(pady=5)
volume_bar['value'] = audio_volume

# 啟動通訊執行緒
threading.Thread(target=serial_listen, daemon=True).start()
root.mainloop()