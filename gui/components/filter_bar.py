import tkinter as tk
from tkinter import ttk
import config

class FilterBarFrame(tk.Frame):
    def __init__(self, parent, on_filter_change_callback, on_export_callback, on_settings_callback=None):
        super().__init__(parent, bg=config.THEME_PANEL_BG, padx=15, pady=8)

        self.on_filter_change = on_filter_change_callback

        # 1. 威脅下拉選單
        tk.Label(self, text="🔍 威脅過濾:", bg=config.THEME_PANEL_BG, fg=config.COLOR_PRIMARY, font=(config.FONT_FAMILY, 9, "bold")).pack(side="left", padx=(0, 5))
        
        self.combo_filter = ttk.Combobox(
            self, 
            values=["全部 (ALL)", "SQL Injection", "Cross-Site Scripting (XSS)", "Path Traversal", "Scanner Detected"],
            state="readonly",
            width=20
        )
        self.combo_filter.current(0)
        self.combo_filter.pack(side="left", padx=(0, 15))
        self.combo_filter.bind("<<ComboboxSelected>>", self.on_filter_change)

        # 2. 關鍵字 / IP 搜尋框
        tk.Label(self, text="🔎 搜尋:", bg=config.THEME_PANEL_BG, fg=config.COLOR_PRIMARY, font=(config.FONT_FAMILY, 9, "bold")).pack(side="left", padx=(0, 5))
        
        self.entry_search = tk.Entry(self, bg="#181818", fg="#FFFFFF", insertbackground="white", width=18, font=(config.FONT_FAMILY, 9))
        self.entry_search.pack(side="left", padx=(0, 15))
        self.entry_search.bind("<KeyRelease>", self.on_filter_change)

        # 3. 筆數統計
        self.lbl_count = tk.Label(self, text="顯示: 0/0 筆", bg=config.THEME_PANEL_BG, fg="#AAAAAA", font=(config.FONT_FAMILY, 9))
        self.lbl_count.pack(side="right", padx=(10, 0))

        # 4. ⚙️ 連線設定按鈕
        if on_settings_callback:
            self.btn_settings = tk.Button(
                self, 
                text="⚙️ 連線設定", 
                command=on_settings_callback,
                bg="#333333", 
                fg="#00FF88", 
                font=(config.FONT_FAMILY, 9, "bold"),
                relief="flat",
                padx=8,
                pady=2
            )
            self.btn_settings.pack(side="right", padx=5)

        # 5. 匯出 CSV 按鈕
        self.btn_export = tk.Button(
            self, 
            text="💾 匯出 CSV", 
            command=on_export_callback,
            bg="#005588", 
            fg="#FFFFFF", 
            font=(config.FONT_FAMILY, 9, "bold"),
            relief="flat",
            padx=8,
            pady=2
        )
        self.btn_export.pack(side="right", padx=5)

        # ⚠️ 關鍵：確保工具列會顯示在畫面上
        self.pack(fill="x", padx=15, pady=5)

    def get_filter_criteria(self):
        return self.combo_filter.get(), self.entry_search.get()

    def update_count(self, visible_count, total_count):
        self.lbl_count.config(text=f"顯示: {visible_count}/{total_count} 筆")