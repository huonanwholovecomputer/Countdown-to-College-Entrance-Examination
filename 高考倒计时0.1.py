import tkinter as tk
from datetime import datetime

# 目标日期
target_date = datetime(2025, 6, 7)

def update_countdown():
    now = datetime.now()
    remaining_time = target_date - now
    days = remaining_time.days
    countdown_text.set(f"{days+1}天")

# 创建主窗口
root = tk.Tk()
root.title("距离2025年高考还有")

# 倒计时标签
countdown_text = tk.StringVar()
label = tk.Label(root, textvariable=countdown_text, font=("Helvetica", 80))
label.pack()

# 开始更新倒计时
update_countdown()

# 运行主循环
root.mainloop()
