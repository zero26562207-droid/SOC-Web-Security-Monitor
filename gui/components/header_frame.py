import tkinter as tk
import config

class HeaderFrame(tk.LabelFrame):
    def __init__(self, parent):
        super().__init__(
            parent, text=" 系統狀態彙整 ", fg=config.COLOR_PRIMARY, 
            bg=config.THEME_BG, font=(config.FONT_FAMILY, 11, 'bold'), padx=15, pady=8
        )
        self.pack(fill="x", padx=15, pady=5)

        self.lbl_status = tk.Label(self, text="● 狀態: 初始化中...", fg=config.COLOR_WARN, bg=config.THEME_BG, font=(config.FONT_FAMILY, 10, 'bold'))
        self.lbl_status.pack(side="left", padx=10)

        self.lbl_logs = tk.Label(self, text="已處理日誌: 0 列", fg=config.COLOR_TEXT, bg=config.THEME_BG, font=(config.FONT_FAMILY, 10))
        self.lbl_logs.pack(side="left", padx=20)

        self.lbl_alerts = tk.Label(self, text="累計觸發威脅: 0 次", fg=config.COLOR_ALERT, bg=config.THEME_BG, font=(config.FONT_FAMILY, 10, 'bold'))
        self.lbl_alerts.pack(side="left", padx=20)

    def update_status(self, status_text, log_count):
        fg = config.COLOR_PRIMARY if "正常" in status_text else config.COLOR_WARN
        self.lbl_status.config(text=f"● 狀態: {status_text}", fg=fg)
        self.lbl_logs.config(text=f"已處理日誌: {log_count} 列")

    def update_alerts_count(self, count):
        self.lbl_alerts.config(text=f"累計觸發威脅: {count} 次")