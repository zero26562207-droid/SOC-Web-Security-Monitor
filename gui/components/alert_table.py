import tkinter as tk
from tkinter import ttk
import config

class AlertTableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.THEME_BG)
        self.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("time", "threat", "ip", "request")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("time", text="時間")
        self.tree.heading("threat", text="威脅類型")
        self.tree.heading("ip", text="來源 IP")
        self.tree.heading("request", text="HTTP 存取紀錄 (URL Decoded)")

        self.tree.column("time", width=100, anchor="center")
        self.tree.column("threat", width=180, anchor="center")
        self.tree.column("ip", width=140, anchor="center")
        self.tree.column("request", width=600, anchor="w")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.tag_configure('alert_row', foreground='#ff6666', background='#3a2222')

    def render_data(self, alert_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for alert in alert_list:
            self.tree.insert("", "end", values=(alert['time'], alert['threat'], alert['ip'], alert['request']), tags=('alert_row',))