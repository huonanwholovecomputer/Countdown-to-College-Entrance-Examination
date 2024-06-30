from tkinter import simpledialog, Tk, Label, font  # 提供简单的对话框、Tkinter主窗口、标签组件和字体管理
from datetime import datetime, timedelta  # 提供日期和时间的处理
from pystray import MenuItem as item  # 右键菜单相关模块
from PIL import Image, ImageTk  # 提供图像处理功能和Tkinter兼容的图像显示
import win32com.client  # 提供访问Windows COM对象的接口
import threading  # 提供线程管理和同步支持
import pyautogui  # 提供获取屏幕分辨率功能
import pystray  # 提供创建系统托盘图标的功能
import socket  # 提供网络套接字通信功能
import ctypes  # 提供调用C语言类型库的接口
import json  # 提供JSON数据编码和解码功能
import sys  # 提供获取当前可执行文件的路径的功能
import os  # 提供操作系统依赖的接口函数

# 设置 DPI 感知，改善在高 DPI 设置下的显示效果
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# 程序的运行标识，用于接收"show"信息
HOST = "localhost"
PORT = 65432

# 初始化[date_year]变量
now = datetime.now()
gaokao_month = 6
gaokao_day = 7
if now.month > gaokao_month or (now.month == gaokao_month and now.day >= gaokao_day):
    date_year = now.year + 1
else:
    date_year = now.year

# 初始化[选择高考年份]函数中的相关的变量
year_1 = date_year
year_2 = date_year + 1
year_3 = date_year + 2

# 构建相关文件的目录
program_data_storage_directory = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Countdown_software")
os.makedirs(program_data_storage_directory, exist_ok=True)
config_path = os.path.join(program_data_storage_directory, "config.json")
shortcut_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\2025高考倒计时.lnk"
# 获取程序所在目录
if getattr(sys, 'frozen', False):  # 如果程序被打包成了EXE
    exe_path = os.path.dirname(sys.executable)
else:  # 如果程序在解释器中运行
    exe_path = os.path.dirname(os.path.abspath(__file__))

# 定义一个名为GUI的类
class GUI:
    # __init__ 方法是一个特殊的方法，当创建类的新实例时自动调用。这个方法内的 self 参数代表类的实例本身。
    def __init__(self, date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down):
        self.root = Tk()
        self.title_name = title_name
        self.root.title(self.title_name)
        self.root.protocol("WM_DELETE_WINDOW", self.toggle_window_visibility)
        self.running = True  # 控制循环的标识
        self.initialize(date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down)  # 初始化界面
        self.create_systray_icon()  # 添加菜单和图标
        self.update_time()
        threading.Thread(target=self.handle_requests, daemon=True).start()  # 启动处理请求的线程（多线程）

    # 初始化Tkinter主界面
    def initialize(self, date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down):
        self.date_year = date_year
        self.title_name = title_name
        self.condition = condition
        self.root.overrideredirect(self.condition)  # 窗口装饰
        self.font_name = font_name
        self.font_size = font_size
        custom_font = font.Font(family=self.font_name, size=self.font_size)  # 字体、字体大小
        self.custom_font = custom_font
        self.time_format = time_format
        self.time_label = Label(self.root, text="", font=self.custom_font, width=50)  # 创建标签用于显示内容
        self.time_label.pack(pady=0)  # 放置标签
        self.window_width, self.window_height, self.position_right, self.position_down = window_width, window_height, position_right, position_down
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.position_right}+{self.position_down}")  # 窗口位置、大小
        self.time_label.pack(pady=0)

    # def 更新时间
    def update_time(self):
        if not self.running:
            return
        now = datetime.now()
        target_date = datetime(self.date_year, 6, 7)
        countdown = target_date - now
        self.days, seconds = countdown.days, countdown.seconds
        self.hours = seconds // 3600
        self.minutes = (seconds % 3600) // 60
        self.seconds = seconds % 60
        total_days = countdown.days
        current_date = now
        months = 0
        while current_date < target_date:
            month_days = (current_date + timedelta(days=32)).replace(day=1) - current_date.replace(day=1)
            if current_date + month_days > target_date:
                break
            months += 1
            current_date += month_days
        self.months = months
        self.weeks = total_days // 7
        if self.time_format == 1:
            time_str = f"{self.days} 天 {self.hours} 小时 {self.minutes} 分 {self.seconds} 秒"
        elif self.time_format == 2:
            time_str = f"{self.days} 天 {self.hours} 小时 {self.minutes+1} 分"
        elif self.time_format == 3:
            time_str = f"{self.days} 天 {self.hours+1} 小时"
        elif self.time_format == 4:
            time_str = f"{self.days+1} 天"
        elif self.time_format == 5:
            time_str = f"{self.months} 月 {self.days % 30} 天 {self.hours} 时 {self.minutes} 分 {self.seconds} 秒"
        elif self.time_format == 6:
            time_str = f"{self.months} 月 {self.days % 30} 天 {self.hours} 时 {self.minutes+1} 分"
        elif self.time_format == 7:
            time_str = f"{self.months} 月 {self.days % 30} 天 {self.hours+1} 时"
        elif self.time_format == 8:
            time_str = f"{self.months} 月 {self.days % 30 + 1} 天"
        elif self.time_format == 9:
            time_str = f"{self.months+1} 月"
        elif self.time_format == 10:
            time_str = f"{self.weeks} 周 {self.days % 7} 天 {self.hours} 时 {self.minutes} 分 {self.seconds} 秒"
        elif self.time_format == 11:
            time_str = f"{self.weeks} 周 {self.days % 7} 天 {self.hours} 时 {self.minutes+1} 分"
        elif self.time_format == 12:
            time_str = f"{self.weeks} 周 {self.days % 7} 天 {self.hours+1} 时"
        elif self.time_format == 13:
            time_str = f"{self.weeks} 周 {self.days % 7 + 1} 天"
        elif self.time_format == 14:
            time_str = f"{self.weeks+1} 周"
        self.time_label.config(text=time_str)
        now = datetime.now()
        next_second = (now + timedelta(seconds=1)).replace(microsecond=0)
        delay = (next_second - now).total_seconds() * 1000
        self.root.after(int(delay), self.update_time)

# 右键菜单-显示/隐藏

    # def 显示/隐藏窗口
    def toggle_window_visibility(self, icon=None, item=None):
        if self.root.state() == "withdrawn":
            self.show_window()
        else:
            self.hide_window()

    # def 隐藏窗口
    def hide_window(self):
        self.root.withdraw()  # 隐藏窗口

    # def 显示窗口
    def show_window(self):
        self.icon.visible = True
        self.root.deiconify()  # 恢复窗口
        self.root.state("normal")  # 确保窗口恢复正常状态

# 右键菜单-转换桌面窗口模式

    # def 转换Tkinter窗口模式
    def conversion(self):
        self.condition = not self.condition
        self.root.overrideredirect(self.condition)

# 右键菜单-时间格式

    # def 修改时间格式
    def change_time_format(self, format_type):
        format_dict = {
            1: f"{self.days} 天 {self.hours} 小时 {self.minutes} 分 {self.seconds} 秒",
            2: f"{self.days} 天 {self.hours} 小时 {self.minutes+1} 分",
            3: f"{self.days} 天 {self.hours+1} 小时",
            4: f"{self.days+1} 天",
            5: f"{self.months} 月 {self.days % 30} 天 {self.hours} 时 {self.minutes} 分 {self.seconds} 秒",
            6: f"{self.months} 月 {self.days % 30} 天 {self.hours} 时 {self.minutes+1} 分",
            7: f"{self.months} 月 {self.days % 30} 天 {self.hours+1} 时",
            8: f"{self.months} 月 {self.days % 30 + 1} 天",
            9: f"{self.months+1} 月",
            10: f"{self.weeks} 周 {self.days % 7} 天 {self.hours} 时 {self.minutes} 分 {self.seconds} 秒",
            11: f"{self.weeks} 周 {self.days % 7} 天 {self.hours} 时 {self.minutes+1} 分",
            12: f"{self.weeks} 周 {self.days % 7} 天 {self.hours+1} 时",
            13: f"{self.weeks} 周 {self.days % 7 + 1} 天",
            14: f"{self.weeks+1} 周"
        }
        self.time_label.config(text=format_dict[format_type])
        self.time_format = format_type

# 右键菜单-其他设置-开机自启动

    # def 获取lnk文件内部指向的exe程序路径
    def get_shortcut_target(shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        return os.path.abspath(shortcut.TargetPath)

    # def 创建程序快捷方式
    def create_shortcut(self, exe_path, shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.save()

    # def 删除快捷方式
    def remove_shortcut(self, shortcut_path):
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            
    # def 检测快捷方式是否存在
    def is_shortcut_exist(self):
        return os.path.exists(shortcut_path)

    # def "开机自启动"右键菜单主逻辑
    def toggle_autostart(self):
        if os.path.exists(shortcut_path):
            self.remove_shortcut(shortcut_path)
        else:
            self.create_shortcut(exe_path, shortcut_path)

# 右键菜单-其他设置-字体大小

    # def 修改字体大小
    def change_font_size(self):
        size_list = list(range(font_size - 15, font_size + 16))
        def make_font_size_item(size):
            return pystray.MenuItem(str(size),lambda: self.set_font_size(size),checked=lambda item: self.font_size == size)
        font_size_menu_items = [make_font_size_item(size) for size in size_list]
        return pystray.Menu(*font_size_menu_items)

    # def 设置字体大小选择回调函数
    def set_font_size(self, size):
        self.running = False  # 停止当前的时间更新
        self.time_label.destroy()  # 摧毁tkinter窗口现有的标签
        self.font_size = size
        self.initialize(self.date_year, self.title_name, self.condition, self.font_name, self.font_size, self.time_format, self.window_width, self.window_height, self.position_right, self.position_down)
        self.running = True  # 恢复时间更新
        self.update_time()  # 重新启动时间更新

# 右键菜单-其他设置-字体

    # 获取系统字体（排除带"@"和英文名字的字体）
    def get_system_fonts(self):
        font_names = list(font.families())
        filtered_fonts = [name for name in font_names if "@" not in name and not name.isascii()]
        return sorted(set(filtered_fonts))

    # def 设置字体选择回调函数
    def set_font(self, font_name):
        self.running = False  # 停止当前的时间更新
        self.time_label.destroy()  # 摧毁tkinter窗口现有的标签
        self.font_name = font_name
        self.initialize(self.date_year, self.title_name, self.condition, self.font_name, self.font_size, self.time_format, self.window_width, self.window_height, self.position_right, self.position_down)
        self.running = True  # 恢复时间更新
        self.update_time()  # 重新启动时间更新

    # def 生成字体菜单
    def create_font_menu(self):
        fonts = self.get_system_fonts()
        def make_font_item(font_name):
            return pystray.MenuItem(font_name, lambda: self.set_font(font_name), checked=lambda item: self.font_name == font_name)
        font_menu_items = [make_font_item(font_name) for font_name in fonts]
        return pystray.Menu(*font_menu_items)

# 右键菜单-其他设置-高考年份

    # def 应用[date_year]变量
    def return_date_year(self, year):
        self.running = False  # 停止当前的时间更新
        self.time_label.destroy()  # 摧毁tkinter窗口现有的标签
        self.date_year = year
        self.initialize(self.date_year, self.title_name, self.condition, self.font_name, self.font_size, self.time_format, self.window_width, self.window_height, self.position_right, self.position_down)
        self.running = True  # 恢复时间更新
        self.update_time()  # 重新启动时间更新

# 右键菜单-其他设置-恢复出厂设置

    # def 恢复出厂设置
    def restore_factory_settings(self):
        self.running = False  # 停止当前的时间更新
        self.time_label.destroy()  # 摧毁tkinter窗口现有的标签
        self.date_year, self.title_name, self.condition, self.font_name, self.font_size, self.time_format, self.window_width, self.window_height, self.position_right, self.position_down = Default_setting()
        self.initialize(self.date_year, self.title_name, self.condition, self.font_name, self.font_size, self.time_format, self.window_width, self.window_height, self.position_right, self.position_down)
        self.running = True  # 恢复时间更新
        self.update_time()  # 重新启动时间更新

    # def 退出程序
    def quit_window(self, icon: pystray.Icon, item=None):
        # 获取窗口的位置和尺寸
        self.position_right, self.position_down = self.root.winfo_x(), self.root.winfo_y()
        self.window_width, self.window_height = self.root.winfo_width(), self.root.winfo_height()
        self.running = False  # 停止更新循环
        self.root.after(0, self._quit_window)  # 在主线程中执行退出操作

    # def 结束所有活动
    def _quit_window(self):
        self.icon.stop()  # 停止 Pystray 的事件循环
        self.root.quit()  # 终止 Tkinter 的事件循环
        self.root.destroy()  # 销毁应用程序的主窗口和所有活动

    # def 创建托盘图标及右键菜单
    def create_systray_icon(self):
        precision_submenu_1 = pystray.Menu(
            pystray.MenuItem("天/时/分/秒", lambda: self.change_time_format(1), checked=lambda item: self.time_format == 1),
            pystray.MenuItem("天/时/分", lambda: self.change_time_format(2), checked=lambda item: self.time_format == 2),
            pystray.MenuItem("天/时", lambda: self.change_time_format(3), checked=lambda item: self.time_format == 3),
            pystray.MenuItem("天", lambda: self.change_time_format(4), checked=lambda item: self.time_format == 4),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("月/天/时/分/秒", lambda: self.change_time_format(5), checked=lambda item: self.time_format == 5),
            pystray.MenuItem("月/天/时/分", lambda: self.change_time_format(6), checked=lambda item: self.time_format == 6),
            pystray.MenuItem("月/天/时", lambda: self.change_time_format(7), checked=lambda item: self.time_format == 7),
            pystray.MenuItem("月/天", lambda: self.change_time_format(8), checked=lambda item: self.time_format == 8),
            pystray.MenuItem("月", lambda: self.change_time_format(9), checked=lambda item: self.time_format == 9),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("周/天/时/分/秒", lambda: self.change_time_format(10), checked=lambda item: self.time_format == 10),
            pystray.MenuItem("周/天/时/分", lambda: self.change_time_format(11), checked=lambda item: self.time_format == 11),
            pystray.MenuItem("周/天/时", lambda: self.change_time_format(12), checked=lambda item: self.time_format == 12),
            pystray.MenuItem("周/天", lambda: self.change_time_format(13), checked=lambda item: self.time_format == 13),
            pystray.MenuItem("周", lambda: self.change_time_format(14), checked=lambda item: self.time_format == 14),
        )
        precision_submenu_2_1 = pystray.Menu(
            pystray.MenuItem(str(year_1), lambda: self.return_date_year(year_1), checked=lambda item: self.date_year == year_1),
            pystray.MenuItem(str(year_2), lambda: self.return_date_year(year_2), checked=lambda item: self.date_year == year_2),
            pystray.MenuItem(str(year_3), lambda: self.return_date_year(year_3), checked=lambda item: self.date_year == year_3)
        )
        precision_submenu_2 = pystray.Menu(
            pystray.MenuItem("开机自启动", self.toggle_autostart, checked=lambda item: self.is_shortcut_exist()),
            pystray.MenuItem("字体大小", self.change_font_size()),
            pystray.MenuItem("字体", self.create_font_menu()),
            pystray.MenuItem("高考年份",precision_submenu_2_1),
            pystray.MenuItem("恢复出厂设置", self.restore_factory_settings)
        )
        main_menu = pystray.Menu(
            pystray.MenuItem("显示/隐藏", self.toggle_window_visibility, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("切换桌面窗口模式", self.conversion),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("时间格式", precision_submenu_1),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("其他设置", precision_submenu_2),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self.quit_window)
        )
        image = Image.open("_internal\\image.ico")
        self.icon = pystray.Icon("icon", image, "高考倒计时", main_menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    # def 接收信息的端口
    def handle_requests(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if data == b"show":
                        self.show_window()

    # def 发送"显示窗口"的信息：进程间通信
    def send_show_request(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                s.sendall(b"show")
                return True
            except ConnectionRefusedError:
                return False

# 默认配置
def Default_setting():
    title_name = f"距离{date_year}年高考还有"

    # 初始化Tkinter主窗口模式
    condition = False  # Tkinter窗口的取消装饰: 值设置为: [False](即添加窗口装饰)
    time_format = 1  # 时间格式为"天/时/分/秒"
    font_name = "Microsoft YaHei"  # 字体为"Microsoft YaHei"

    # 获取屏幕分辨率
    screen_width, screen_height = pyautogui.size()
    
    # 基准窗口宽度、高度、字体大小
    base_window_width = 3000
    base_window_height = 300
    base_font_size = 60

    # 调用 Windows API 函数获取缩放比例
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    scaling_factor = user32.GetDpiForSystem()
    current_windows_scaling_factor = scaling_factor / 96.0

    # 比例
    width_scale = screen_width / 3840
    height_scale = screen_height / 2160
    font_size_scale = current_windows_scaling_factor / 3.0

    # 用窗口比例计算窗口大小、字体大小
    window_width = int(base_window_width * width_scale)
    window_height = int(base_window_height * height_scale)
    font_size = int(base_font_size * height_scale)
    
    # 调整字体大小以适应当前系统缩放比例
    font_size = int(font_size / font_size_scale)

    # 计算窗口位置（默认水平居中、上移40%高度）
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2 - screen_height * 0.4)

    # 返回所有的变量
    return date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down

# 接收"显示窗口"的信息：进程间通信
def send_show_request():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(b'show')
            return True
        except ConnectionRefusedError:
            return False

# 主程序
if __name__ == "__main__":
    if not send_show_request():  # 如果发送"show"失败
        if os.path.exists(config_path):  # 如果配置文件存在
            # 尝试加载已有的配置
            try:
                with open(config_path, "r", encoding="utf-8") as file:
                    config_data = json.load(file)
                    date_year = config_data.get("高考年份")
                    title_name = config_data.get("标题名称")
                    condition = config_data.get("窗口模式")
                    font_name = config_data.get("字体")
                    font_size = config_data.get("字体大小")
                    time_format = config_data.get("时间格式")
                    position_right = config_data.get("窗口位置(右)")
                    position_down = config_data.get("窗口位置(下)")
                    window_width = config_data.get("窗口宽度")
                    window_height = config_data.get("窗口高度")
            except json.JSONDecodeError:  # 如果配置文件损坏
                os.remove(config_path)  # 移除配置文件
                date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down = Default_setting()
        else:  # 如果配置文件不存在
            date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down = Default_setting()

        gui = GUI(date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down)
        gui.root.mainloop()

        # 程序结束时保存配置
        config_data = {
            "高考年份": gui.date_year,
            "标题名称": gui.title_name,
            "窗口模式": gui.condition,
            "字体大小": gui.font_size,
            "字体": gui.font_name,
            "时间格式": gui.time_format,
            "窗口位置(右)": gui.position_right,
            "窗口位置(下)": gui.position_down,
            "窗口宽度": gui.window_width,
            "窗口高度": gui.window_height
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as config_file:
            json.dump(config_data, config_file, ensure_ascii=False, indent=4)
