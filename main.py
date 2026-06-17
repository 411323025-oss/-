import time
from machine import Pin, ADC
import sys
import uselect

# 1. 初始化劇院搖桿
joy_x = ADC(Pin(36))  # 核心板左上角 VP 腳位
joy_y = ADC(Pin(35))  # 核心板左側 IO34 腳位
joy_x.atten(ADC.ATTN_11DB)
joy_y.atten(ADC.ATTN_11DB)

# 2. 初始化兩個實體快捷按鈕
btn_theater = Pin(25, Pin.IN, Pin.PULL_UP) # 按鈕 1：切換劇院情境
btn_mute = Pin(27, Pin.IN, Pin.PULL_UP)  # 按鈕 2：一鍵靜音/復位

# 3. 實體劇院環境指示燈
green_led = Pin(13, Pin.OUT)  # 綠燈：普通明亮模式
yellow_led = Pin(12, Pin.OUT) # 黃燈：影院調暗模式
green_led.value(1)
yellow_led.value(0)

# 設定非阻塞序列埠監聽
poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

while True:
    # 監聽電腦端傳回的燈號切換指令
    if poller.poll(0):
        cmd = sys.stdin.readline().strip()
        if cmd == "LED_THEATER":
            green_led.value(0)
            yellow_led.value(1)
        elif cmd == "LED_NORMAL":
            green_led.value(1)
            yellow_led.value(0)
            
    # 讀取搖桿類比數值 (0 ~ 4095)
   # 讀取搖桿類比數值 (連續讀兩次，清除內部 ADC 電容干擾)
    joy_x.read()          # 第一次空讀（丟棄）
    val_x = joy_x.read()  # 第二次才是乾淨的 X 軸數據
    
    joy_y.read()          # 第一次空讀（丟棄）
    val_y = joy_y.read()  # 第二次才是乾淨的 Y 軸數據
    
    # 讀取實體按鈕狀態 (未按為 0，按下為 1)
    state_the = "1" if btn_theater.value() == 0 else "0"
    state_mut = "1" if btn_mute.value() == 0 else "0"
    
    # 將手勢與按鈕控制訊號即時傳送給遠端電腦
    print(f"X:{val_x},Y:{val_y},THE:{state_the},MUT:{state_mut}")
    
    time.sleep(0.05)  # 20Hz 高速刷新，手感才會流暢