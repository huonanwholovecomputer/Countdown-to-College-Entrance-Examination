try:
    from tkinter import simpledialog, Tk, Label, font, Toplevel, Text, Frame, Button, END  # 提供简单的对话框、Tkinter主窗口、标签组件和字体管理等
    from dateutil.relativedelta import relativedelta  # 提供日期、时间的计算
    from datetime import datetime, timedelta  # 提供日期和时间的处理
    from pystray import MenuItem as item  # 右键菜单相关模块
    import win32com.shell.shell as shell  # 用于执行与管理员权限相关的操作
    from plyer import notification  # 显示Windows通知相关功能
    from PIL import Image, ImageTk  # 提供图像处理功能和Tkinter兼容的图像显示
    import win32com.client  # 提供访问Windows COM对象的接口
    import threading  # 提供线程管理和同步支持
    import traceback  # 提供详细的错误日志功能
    import pyautogui  # 提供获取屏幕分辨率功能
    import pystray  # 提供创建系统托盘图标的功能
    import logging  # 捕捉错误信息
    import random  # 随机选择
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
    def calculate_date_year():
        now = datetime.now()
        gaokao_month = 6
        gaokao_day = 7
        if now.month > gaokao_month or (now.month == gaokao_month and now.day >= gaokao_day):
            return now.year + 1
        else:
            return now.year
    date_year = calculate_date_year()

    # 初始化[选择高考年份]函数中的相关的变量
    year_1 = date_year
    year_2 = date_year + 1
    year_3 = date_year + 2

    # 初始化剩余天数
    now = datetime.now()
    target_date = datetime(date_year, 6, 7)
    countdown = target_date - now
    countdown_days = countdown.days

    # 获取程序地址（用于快捷方式的创建）
    if getattr(sys, 'frozen', False):
        # 如果程序被打包成了EXE
        exe_path = sys.executable
    else:
        # 如果程序在解释器中运行
        exe_path = os.path.abspath(__file__)

    # 获取程序所在目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        exe_dir = os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # 构建相关文件的目录
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    program_data_storage_directory = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Countdown_software")
    os.makedirs(program_data_storage_directory, exist_ok=True)
    config_path = os.path.join(program_data_storage_directory, "config.json")
    shortcut_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\2025高考倒计时.lnk"
    icon_path = os.path.join(exe_path, "_internal", "icon.ico")
    message_path = os.path.join(program_data_storage_directory, "message文案.txt")

    # 定义一个名为GUI的类
    class GUI:
        # __init__ 方法是一个特殊的方法，当创建类的新实例时自动调用。这个方法内的 self 参数代表类的实例本身。
        def __init__(self, date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down, notificing_setting):
            self.root = Tk()
            self.notificing_setting = notificing_setting
            self.title_name = title_name  # self内部变量赋值
            self.root.title(self.title_name)
            self.root.protocol("WM_DELETE_WINDOW", self.toggle_window_visibility)
            self.running = True  # 控制循环的标识
            self.initialize(date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down)  # 初始化界面
            self.create_systray_icon()  # 添加菜单和图标
            self.update_time()  # 开始更新时间
            threading.Thread(target=self.handle_requests, daemon=True).start()  # 启动处理请求的线程（多线程）

        # 初始化Tkinter主界面
        def initialize(self, date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down):
            self.date_year = date_year  # self内部变量赋值
            self.title_name = title_name  # self内部变量赋值
            self.condition = condition  # self内部变量赋值
            self.root.overrideredirect(self.condition)  # 窗口装饰
            self.font_name = font_name  # self内部变量赋值
            self.font_size = font_size  # self内部变量赋值
            custom_font = font.Font(family=self.font_name, size=self.font_size)  # 字体、字体大小
            self.custom_font = custom_font  # self内部变量赋值
            self.time_label = Label(self.root, text="", font=self.custom_font, width=50)  # 创建标签用于显示内容
            self.time_format = time_format  # self内部变量赋值
            self.window_width, self.window_height, self.position_right, self.position_down = window_width, window_height, position_right, position_down  # self内部变量赋值
            self.root.geometry(f"{self.window_width}x{self.window_height}+{self.position_right}+{self.position_down}")  # 设置窗口位置、大小
            self.time_label.pack(pady=0)  # 放置标签

        # 更新时间
        def update_time(self):
            if not self.running:
                return
            # 计算日期、时间
            now = datetime.now()
            target_date = datetime(self.date_year, 6, 7)
            countdown = target_date - now
            self.days, seconds = countdown.days, countdown.seconds
            self.hours = seconds // 3600
            self.minutes = (seconds % 3600) // 60
            self.seconds = seconds % 60
            total_days = countdown.days
            rd = relativedelta(target_date, now)
            months = rd.months
            self.months = months
            self.weeks = total_days // 7

            # 时间格式的处理
            if self.time_format == 1:
                time_str = f"{self.days} 天 {self.hours} 小时 {self.minutes} 分 {self.seconds} 秒"
            elif self.time_format == 2:
                time_str = f"{self.days} 天 {self.hours} 小时 {self.minutes+1} 分"
            elif self.time_format == 3:
                time_str = f"{self.days} 天 {self.hours+1} 小时"
            elif self.time_format == 4:
                time_str = f"{self.days+1} 天"
            elif self.time_format == 5:
                time_str = f"{self.months} 月 {rd.days} 天 {self.hours} 时 {self.minutes} 分 {self.seconds} 秒"
            elif self.time_format == 6:
                time_str = f"{self.months} 月 {rd.days} 天 {self.hours} 时 {self.minutes+1} 分"
            elif self.time_format == 7:
                time_str = f"{self.months} 月 {rd.days} 天 {self.hours+1} 时"
            elif self.time_format == 8:
                time_str = f"{self.months} 月 {rd.days + 1} 天"
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

            # 更新时间格式
            self.time_label.config(text=time_str)

            # 计算下一次更新倒计时的时间（用于相对系统时间精确到秒）
            now = datetime.now()
            next_second = (now + timedelta(seconds=1)).replace(microsecond=0)
            delay = (next_second - now).total_seconds() * 1000
            self.root.after(int(delay), self.update_time)

    # 右键菜单-显示/隐藏

        # 显示/隐藏窗口
        def toggle_window_visibility(self, icon=None, item=None):
            if self.root.state() == "withdrawn":
                self.show_window()
            else:
                self.hide_window()

        # 隐藏窗口
        def hide_window(self):
            self.root.withdraw()  # 隐藏窗口

        # 显示窗口
        def show_window(self):
            self.icon.visible = True
            self.root.deiconify()  # 恢复窗口
            self.root.state("normal")  # 确保窗口恢复正常状态

    # 右键菜单-转换桌面窗口模式

        # 转换Tkinter窗口模式
        def conversion(self):
            self.condition = not self.condition
            self.root.overrideredirect(self.condition)

    # 右键菜单-时间格式

        # 修改时间格式
        def change_time_format(self, format_type):
            self.time_format = format_type

    # 右键菜单-其他设置-开机自启动

        # 创建程序快捷方式
        def create_shortcut(self, exe_path, shortcut_path):
            startup_dir = os.path.dirname(shortcut_path)
            if not os.path.exists(startup_dir):
                os.makedirs(startup_dir)

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.save()

        # 删除快捷方式
        def remove_shortcut(self, shortcut_path):
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)

        # 检测快捷方式是否存在
        def is_shortcut_exist(self):
            return os.path.exists(shortcut_path)

        # "开机自启动"右键菜单主逻辑
        def toggle_autostart(self):
            if self.is_shortcut_exist():
                self.remove_shortcut(shortcut_path)
            else:
                self.create_shortcut(exe_path, shortcut_path)

    # 右键菜单-其他设置-启动时显示通知

        def notification_setting(self, notificing_setting):
            self.notificing_setting = not self.notificing_setting
            self.save_config()  # 保存配置

    # 右键菜单-其他设置-自定义通知文案

        def show_input_window(self, icon, item):
            initial_lines = self.read_message_file(message_path)

            def on_confirm():
                input_messages = text_entry.get("1.0", END).strip()
                with open(message_path, "w", encoding="utf-8") as message_file:
                    message_file.write(input_messages)

                # 发送一条Windows通知
                notification.notify(
                title="保存成功",
                message="自定义文案已成功保存",
                app_name="高考倒计时",
                app_icon=os.path.join(exe_dir, "_internal", "image.ico"),
                timeout=5
                )

                input_window.destroy()

            def on_cancel():
                input_window.destroy()

            # 创建一个新窗口
            input_window = Toplevel(self.root)
            input_window.title("自定义通知文案")

            # 创建文本输入框并设置初始文本
            text_entry = Text(input_window, height=30, width=50)
            text_entry.insert(END, "".join(initial_lines))
            text_entry.pack(pady=0)

            # 按钮框架
            button_frame = Frame(input_window)
            button_frame.pack(pady=10)

            # 创建确认和取消按钮
            confirm_button = Button(button_frame, text="确认", command=on_confirm)
            confirm_button.pack(side="left", padx=25)
            cancel_button = Button(button_frame, text="取消", command=on_cancel)
            cancel_button.pack(side="left", padx=25)

        def read_message_file(self, file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.readlines()

    # 右键菜单-其他设置-保存当前所有配置

        def save_config(self):

            # 转换变量
            if self.notificing_setting == True:
                self.notifice_setting = "是"
            elif self.notificing_setting == False:
                self.notifice_setting = "否"

            # 获取窗口的位置和尺寸
            self.position_right, self.position_down = self.root.winfo_x(), self.root.winfo_y()
            self.window_width, self.window_height = self.root.winfo_width(), self.root.winfo_height()

            config_data = {
                "高考年份": self.date_year,
                "标题名称": self.title_name,
                "窗口模式": self.condition,
                "字体大小": self.font_size,
                "字体": self.font_name,
                "时间格式": self.time_format,
                "窗口位置(右)": self.position_right,
                "窗口位置(下)": self.position_down,
                "窗口宽度": self.window_width,
                "窗口高度": self.window_height,
                "启动时显示倒计时天数通知": self.notifice_setting
            }
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as config_file:
                json.dump(config_data, config_file, ensure_ascii=False, indent=4)

            # 发送一条Windows通知
            notification.notify(
                title="配置已保存",
                message="您的配置已成功保存。",
                app_name="高考倒计时",
                app_icon=os.path.join(exe_dir, "_internal", "image.ico"),
                timeout=5
            )

    # 右键菜单-其他设置-字体大小

        # 修改字体大小
        def change_font_size(self):
            size_list = list(range(font_size - 15, font_size + 16))
            def make_font_size_item(size):
                return pystray.MenuItem(str(size),lambda: self.set_font_size(size),checked=lambda item: self.font_size == size)
            font_size_menu_items = [make_font_size_item(size) for size in size_list]
            return pystray.Menu(*font_size_menu_items)

        # 设置字体大小选择回调函数
        def set_font_size(self, size):
            self.running = False  # 停止当前的时间更新
            self.time_label.destroy()  # 摧毁tkinter窗口现有的标签
            self.font_size = size
            custom_font = font.Font(family=self.font_name, size=self.font_size)  # 字体、字体大小
            self.custom_font = custom_font  # self内部变量赋值
            self.time_label = Label(self.root, text="", font=self.custom_font, width=50)  # 创建标签用于显示内容
            self.time_label.pack(pady=0)  # 放置标签
            self.running = True  # 恢复时间更新
            self.update_time()  # 重新启动时间更新

    # 右键菜单-其他设置-字体

        # 获取系统字体（排除带"@"和英文名字的字体）
        def get_system_fonts(self):
            font_names = list(font.families())
            filtered_fonts = [name for name in font_names if "@" not in name and not name.isascii()]
            return sorted(set(filtered_fonts))

        # 设置字体选择回调函数
        def set_font(self, font_name):
            self.running = False  # 停止当前的时间更新
            self.time_label.destroy()  # 摧毁tkinter窗口现有的标签
            self.font_name = font_name
            custom_font = font.Font(family=self.font_name, size=self.font_size)  # 字体、字体大小
            self.custom_font = custom_font  # self内部变量赋值
            self.time_label = Label(self.root, text="", font=self.custom_font, width=50)  # 创建标签用于显示内容
            self.time_label.pack(pady=0)  # 放置标签
            self.running = True  # 恢复时间更新
            self.update_time()  # 重新启动时间更新

        # 生成字体菜单
        def create_font_menu(self):
            fonts = self.get_system_fonts()
            def make_font_item(font_name):
                return pystray.MenuItem(font_name, lambda: self.set_font(font_name), checked=lambda item: self.font_name == font_name)
            font_menu_items = [make_font_item(font_name) for font_name in fonts]
            return pystray.Menu(*font_menu_items)

    # 右键菜单-其他设置-高考年份

        # 应用[date_year]变量
        def return_date_year(self, year):
            self.date_year = year

    # 右键菜单-其他设置-恢复出厂设置

        # 恢复出厂设置
        def restore_factory_settings(self):
            self.running = False  # 停止当前的时间更新
            self.time_label.destroy()  # 摧毁tkinter窗口现有的标签
            self.date_year, self.title_name, self.condition, self.font_name, self.font_size, self.time_format, self.window_width, self.window_height, self.position_right, self.position_down, self.notifice_setting = Default_setting()  # 默认设置
            self.initialize(self.date_year, self.title_name, self.condition, self.font_name, self.font_size, self.time_format, self.window_width, self.window_height, self.position_right, self.position_down)  # 初始化Tkinter主界面
            self.running = True  # 恢复时间更新
            self.update_time()  # 重新启动时间更新
            self.save_config()  # 更新配置文件

        # 退出程序
        def quit_window(self, icon: pystray.Icon, item=None):
            self.running = False  # 停止更新循环
            self.root.after(0, self._quit_window)  # 在主线程中执行退出操作

        # 结束所有活动
        def _quit_window(self):
            self.icon.stop()  # 停止 Pystray 的事件循环
            self.root.quit()  # 终止 Tkinter 的事件循环
            self.root.destroy()  # 销毁应用程序的主窗口和所有活动

        # 创建托盘图标及右键菜单
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
                pystray.MenuItem("启动时显示通知",lambda: self.notification_setting(self.notificing_setting), checked=lambda item: self.notificing_setting),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("自定义通知文案", self.show_input_window),
                pystray.MenuItem("保存当前所有配置", self.save_config),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("字体大小", self.change_font_size()),
                pystray.MenuItem("字体", self.create_font_menu()),
                pystray.MenuItem("高考年份",precision_submenu_2_1),
                pystray.Menu.SEPARATOR,
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

        # 接收"显示窗口"的信息：进程间通信
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

    # 发送"显示窗口"的信息：进程间通信
    def send_show_request():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                s.sendall(b'show')
                return True
            except ConnectionRefusedError:
                return False

    # 默认设置
    def Default_setting():
        # 标题名称、是否发送Windows通知
        title_name = f"距离{date_year}年高考还有"
        notifice_setting = "是"

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
        return date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down, notifice_setting

    # 保证以管理员的身份运行程序
    def run_as_admin():
        if shell.IsUserAnAdmin():
            return True  # 已经是管理员权限
        else:
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
            sys.exit(0)  # 退出当前进程

    # 主程序
    if __name__ == "__main__":
        run_as_admin()  #  以管理员身份运行
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
                        notifice_setting = config_data.get("启动时显示倒计时天数通知")

                        # 转换变量
                        if notifice_setting == "是":
                            notificing_setting = True
                        elif notifice_setting == "否":
                            notificing_setting = False

                        # 比较配置文件中的date_year与计算的date_year
                        expected_date_year = calculate_date_year()
                        if date_year < expected_date_year:
                            date_year = expected_date_year  # 更新为当前计算的date_year
                            title_name = f"距离{date_year}年高考还有"
                            # 保存配置
                            config_data = {
                                "高考年份": date_year,
                                "标题名称": title_name,
                                "窗口模式": condition,
                                "字体大小": font_size,
                                "字体": font_name,
                                "时间格式": time_format,
                                "窗口位置(右)": position_right,
                                "窗口位置(下)": position_down,
                                "窗口宽度": window_width,
                                "窗口高度": window_height,
                                "启动时显示倒计时天数通知": notifice_setting
                            }
                            os.makedirs(os.path.dirname(config_path), exist_ok=True)
                            with open(config_path, "w", encoding="utf-8") as config_file:
                                json.dump(config_data, config_file, ensure_ascii=False, indent=4)
                except json.JSONDecodeError:  # 如果配置文件损坏
                    os.remove(config_path)  # 移除配置文件
                    date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down, notifice_setting = Default_setting()  # 默认设置
            else:  # 如果配置文件不存在
                date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down, notificing_setting = Default_setting()  # 默认设置

            # 如果需要显示Windows通知
            if notificing_setting:
                if os.path.exists(message_path):
                    with open(message_path, "r", encoding="utf-8") as message_file:
                        lines = message_file.readlines()
                        message_list = [line.strip() for line in lines]
                    random_message = random.choice(message_list)
                else:
                    default_messages = [
                        "书山有路勤为径，学海无涯苦作舟",
                        "学而不思则罔，思而不学则殆",
                        "宝剑锋从磨砺出，梅花香自苦寒来",
                        "业精于勤荒于嬉，行成于思毁于随",
                        "一分耕耘，一分收获",
                        "学如逆水行舟，不进则退",
                        "饭可以一日不吃，觉可以一日不睡，书不可以一日不读——毛泽东",
                        "要善于提出问题。提出问题往往比解决问题更重要——毛泽东",
                        "读书要善于把书读透，不要做书呆子——毛泽东",
                        "实践是检验真理的唯一标准——毛泽东",
                        "谦虚使人进步，骄傲使人落后——毛泽东",
                        "勤能补拙，笨鸟先飞",
                        "书到用时方恨少，事非经过不知难",
                        "学而时习之，不亦说乎",
                        "不积跬步，无以至千里；不积小流，无以成江海",
                        "天才就是百分之九十九的汗水加上百分之一的灵感",
                        "勤能补拙是良训，一分辛苦一分才",
                        "锲而不舍，金石可镂——《劝学》",
                        "坚持就是胜利",
                        "把努力当成一种习惯",
                        "只要功夫深，铁杵磨成针",
                        "失败乃成功之母",
                        "跌倒了，爬起来继续走",
                        "书中自有黄金屋，书中自有颜如玉",
                        "知识就是力量",
                        "读书破万卷，下笔如有神",
                        "理想是人生的灯塔",
                        "梦想还是要有的，万一实现了呢？",
                        "空想只会停滞不前，行动才能改变一切",
                        "莫等闲，白了少年头，空悲切——岳飞",
                        "天行健，君子以自强不息——《周易》",
                        "吾日三省吾身——《论语》",
                        "Where there is a will, there is a way（有志者，事竟成）",
                        "如果你想成功，首先要相信自己有成功的能力——拿破仑·希尔",
                        "成功不是终点，失败也不是终点，重要的是继续前进的勇气——丘吉尔",
                    ]
                    with open(message_path, "w", encoding="utf-8") as message_file:
                        for message in default_messages:
                            message_file.write(message + "\n")
                    random_message = random.choice(default_messages)

                # 启动时显示倒计时天数
                notification.notify(
                    title=f"{title_name}：{countdown_days+1}天",
                    message=random_message,
                    app_name="高考倒计时",
                    app_icon=os.path.join(exe_dir, "_internal", "image.ico"),
                    timeout=5
                )

            gui = GUI(date_year, title_name, condition, font_name, font_size, time_format, window_width, window_height, position_right, position_down, notificing_setting)  # 为主程序"GUI"输入变量，实例化"GUI"对象

            gui.root.mainloop()  # 启动主事件循环

except Exception as error:
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_file_path = os.path.join(desktop_path, "高考倒计时_错误日志.log")
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format="----------------------------------------\n%(asctime)s - %(levelname)s - %(message)s")

    # 使用 traceback 记录详细的错误信息
    logging.error("\n× 发生了一个错误: %s", str(error))
    logging.error("\n↓详细信息↓", exc_info=True)

    # 发送一条Windows通知
    notification.notify(
    title="× 程序出错！",
    message="请前往桌面的错误日志查看详细信息",
    app_name="高考倒计时",
    app_icon=os.path.join(exe_dir, "_internal", "image.ico"),
    timeout=5
    )
