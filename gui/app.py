import csv
import queue
import re
import datetime
import threading
import urllib.parse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import config
from gui.components.header_frame import HeaderFrame
from gui.components.filter_bar import FilterBarFrame
from gui.components.alert_table import AlertTableFrame
from core.ssh_client import SSHLogMonitor

class SOCAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SOC Web 安全日誌即時防禦系統")
        self.root.geometry("1100x700")
        self.root.configure(bg=config.THEME_BG)

        self.setup_dark_theme()

        self.msg_queue = queue.Queue()
        self.all_alerts = []
        self.alert_items = {}

        # 建立 UI 組件 (傳入 open_settings_dialog 回呼函式)
        self.header = HeaderFrame(self.root)
        self.filter_bar = FilterBarFrame(
            self.root, 
            self.apply_filter, 
            self.export_to_csv,
            on_settings_callback=self.open_settings_dialog
        )
        self.alert_table = AlertTableFrame(self.root)

        # 綁定表格雙擊事件
        self.alert_table.tree.bind("<Double-1>", self.show_threat_detail)

        # 啟動 SSH 背景監控 Thread
        self.start_ssh_monitor()

        self.root.after(100, self.process_queue)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_dark_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#181818",
            foreground="#FF6666",
            fieldbackground="#181818",
            rowheight=26,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#222222",
            foreground="#00FF88",
            font=(config.FONT_FAMILY, 10, "bold"),
            relief="flat"
        )
        style.map("Treeview.Heading", background=[('active', '#333333')])
        style.map("Treeview", background=[('selected', '#550000')], foreground=[('selected', '#FFFFFF')])

    def start_ssh_monitor(self):
        """啟動或重啟 SSH 輪詢執行緒"""
        if hasattr(self, 'monitor') and self.monitor:
            self.monitor.stop()

        self.monitor = SSHLogMonitor(self.msg_queue)
        self.thread = threading.Thread(target=self.monitor.start_polling, daemon=True)
        self.thread.start()

    def open_settings_dialog(self):
        """跳出 IP / Port / SSH 連線自訂輸入視窗"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ 靶機 SSH 連線設定")
        dialog.geometry("450x380")
        dialog.configure(bg="#121212")
        dialog.transient(self.root)
        dialog.grab_set()

        curr = config.load_settings()

        fields = [
            ("靶機 IP 位址 (Host):", "SSH_HOST", curr.get("SSH_HOST", "192.168.56.102")),
            ("SSH 連線 Port 號:", "SSH_PORT", str(curr.get("SSH_PORT", 22))),
            ("SSH 登入帳號:", "SSH_USER", curr.get("SSH_USER", "msfadmin")),
            ("SSH 登入密碼:", "SSH_PASS", curr.get("SSH_PASS", "msfadmin")),
            ("Log 檔案路徑:", "LOG_PATH", curr.get("LOG_PATH", "/var/log/apache2/access.log"))
        ]

        entries = {}
        for idx, (label_text, key, default_val) in enumerate(fields):
            lbl = tk.Label(dialog, text=label_text, bg="#121212", fg="#00FF88", font=(config.FONT_FAMILY, 9, "bold"))
            lbl.grid(row=idx, column=0, sticky="w", padx=20, pady=8)
            
            entry = tk.Entry(dialog, bg="#222222", fg="#FFFFFF", insertbackground="white", font=("Consolas", 10))
            if "PASS" in key:
                entry.config(show="*")
            entry.insert(0, default_val)
            entry.grid(row=idx, column=1, sticky="ew", padx=20, pady=8)
            entries[key] = entry

        dialog.grid_columnconfigure(1, weight=1)

        # ⚠️ 這裡只保留一個 save_and_connect 函式
        def save_and_connect():
            try:
                new_port = int(entries["SSH_PORT"].get().strip())
            except ValueError:
                messagebox.showerror("輸入錯誤", "Port 號必須是整數數字！")
                return

            new_config = {
                "SSH_HOST": entries["SSH_HOST"].get().strip(),
                "SSH_PORT": new_port,
                "SSH_USER": entries["SSH_USER"].get().strip(),
                "SSH_PASS": entries["SSH_PASS"].get().strip(),
                "LOG_PATH": entries["LOG_PATH"].get().strip()
            }
            
            # 1. 寫入 settings.json
            config.save_settings(new_config)
            
            # 2. 同步更新 config 所有相關變數 (含 REMOTE_LOG_PATH)
            config.SSH_HOST = config.HOST = config.IP = config.VM_IP = new_config["SSH_HOST"]
            config.SSH_PORT = config.PORT = config.VM_PORT = new_config["SSH_PORT"]
            config.SSH_USER = config.USER = config.USERNAME = config.VM_USER = new_config["SSH_USER"]
            config.SSH_PASS = config.PASS = config.PASSWORD = config.VM_PASS = new_config["SSH_PASS"]
            config.LOG_PATH = config.REMOTE_LOG_PATH = new_config["LOG_PATH"]

            # 3. 重新建立 SSH 監控
            self.start_ssh_monitor()

            messagebox.showinfo("連線更新", f"連線設定已儲存！\n已嘗試重新連線至 {config.SSH_HOST}:{config.SSH_PORT}")
            dialog.destroy()

        # 🔘 底部按鈕區塊
        btn_frame = tk.Frame(dialog, bg="#121212")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ok_btn = tk.Button(
            btn_frame, 
            text="確定 (儲存並連線)", 
            command=save_and_connect, 
            bg="#008844", 
            fg="#FFFFFF", 
            font=(config.FONT_FAMILY, 9, "bold"), 
            relief="flat", 
            padx=15, 
            pady=5
        )
        ok_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(
            btn_frame, 
            text="取消", 
            command=dialog.destroy, 
            bg="#444444", 
            fg="#FFFFFF", 
            font=(config.FONT_FAMILY, 9, "bold"), 
            relief="flat", 
            padx=15, 
            pady=5
        )
        cancel_btn.pack(side="left", padx=10)

        def save_and_connect():
            try:
                new_port = int(entries["SSH_PORT"].get().strip())
            except ValueError:
                messagebox.showerror("輸入錯誤", "Port 號必須是整數數字！")
                return

            new_config = {
                "SSH_HOST": entries["SSH_HOST"].get().strip(),
                "SSH_PORT": new_port,
                "SSH_USER": entries["SSH_USER"].get().strip(),
                "SSH_PASS": entries["SSH_PASS"].get().strip(),
                "LOG_PATH": entries["LOG_PATH"].get().strip()
            }
            
            # 1. 寫入 settings.json
            config.save_settings(new_config)
            
            # 2. 同步更新 config 所有相關變數
            config.SSH_HOST = config.HOST = config.IP = config.VM_IP = new_config["SSH_HOST"]
            config.SSH_PORT = config.PORT = config.VM_PORT = new_config["SSH_PORT"]
            config.SSH_USER = config.USER = config.USERNAME = config.VM_USER = new_config["SSH_USER"]
            config.SSH_PASS = config.PASS = config.PASSWORD = config.VM_PASS = new_config["SSH_PASS"]
            config.LOG_PATH = config.REMOTE_LOG_PATH = new_config["LOG_PATH"]

            # 3. 重新建立 SSH 監控
            self.start_ssh_monitor()

            messagebox.showinfo("連線更新", f"連線設定已儲存！\n已嘗試重新連線至 {config.SSH_HOST}:{config.SSH_PORT}")
            dialog.destroy()
    def process_queue(self):
        try:
            while True:
                msg_type, data = self.msg_queue.get_nowait()
                if msg_type == "STATUS":
                    status_str, log_count = data
                    self.header.update_status(status_str, log_count)
                elif msg_type == "ALERT":
                    self.add_alert(data)
        except queue.Empty:
            pass

        self.root.after(100, self.process_queue)

    def add_alert(self, alert_data):
        self.all_alerts.append(alert_data)

        timestamp = ""
        threat_type = ""
        src_ip = ""
        http_log = ""

        if isinstance(alert_data, dict):
            timestamp = str(alert_data.get("time") or alert_data.get("timestamp") or alert_data.get("datetime") or "")
            threat_type = str(alert_data.get("type") or alert_data.get("threat_type") or alert_data.get("attack_type") or alert_data.get("rule") or alert_data.get("rule_name") or "")
            src_ip = str(alert_data.get("ip") or alert_data.get("src_ip") or alert_data.get("client_ip") or "")
            http_log = str(alert_data.get("log") or alert_data.get("http_log") or alert_data.get("request") or alert_data.get("raw_log") or "")
        elif isinstance(alert_data, (list, tuple)) and len(alert_data) >= 4:
            timestamp, threat_type, src_ip, http_log = map(str, alert_data[:4])

        raw_text = http_log if http_log else str(alert_data)

        month_map = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }

        time_match = re.search(r'\[(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})\s+([\+\-]\d{4})\]', raw_text)
        if time_match:
            day, month_str, year, hh, mm, ss, tz = time_match.groups()
            m_num = month_map.get(month_str, 1)
            
            dt_log = datetime.datetime(int(year), m_num, int(day), int(hh), int(mm), int(ss))
            
            tz_sign = 1 if tz[0] == '+' else -1
            tz_hours = int(tz[1:3]) * tz_sign
            time_offset = 8 - tz_hours
            dt_taiwan = dt_log + datetime.timedelta(hours=time_offset)
            
            timestamp = dt_taiwan.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not src_ip:
            ip_match = re.search(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', raw_text)
            if ip_match:
                src_ip = ip_match.group(1)

        lower_text = raw_text.lower()
        scanner_keywords = [
            "nmap", "nikto", "masscan", "zgrab", "gobuster", "dirbuster",
            "sqlmap", "wpscan", "nessus", "acunetix", "openvas",
            "hnap1", "evox", "sdk", "nmaplowercheck", "check", "scanner", "bot"
        ]

        if any(kw in lower_text for kw in scanner_keywords):
            threat_type = "Scanner Detected"
        elif "/etc/passwd" in lower_text or "../" in lower_text or "..\\" in lower_text or "page=.." in lower_text or "path" in lower_text:
            threat_type = "Path Traversal"
        elif "script" in lower_text or "alert(" in lower_text or "xss" in lower_text or "<script>" in lower_text:
            threat_type = "Cross-Site Scripting (XSS)"
        elif "or '1'='1" in lower_text or "union" in lower_text or "select" in lower_text or "sql" in lower_text or ("id=" in lower_text and "'" in lower_text):
            threat_type = "SQL Injection"
        else:
            threat_type = "Suspicious Request"

        row_values = (timestamp, threat_type, src_ip, raw_text)

        item_id = self.alert_table.tree.insert("", "end", values=row_values)

        self.alert_items[item_id] = {
            "time": timestamp,
            "type": threat_type.lower(),
            "ip": src_ip.lower(),
            "log": raw_text.lower()
        }

        if hasattr(self.header, 'update_alerts_count'):
            self.header.update_alerts_count(len(self.all_alerts))
        elif hasattr(self.header, 'update_alert_count'):
            self.header.update_alert_count(len(self.all_alerts))

        self.apply_filter()

    def show_threat_detail(self, event):
        selected_item = self.alert_table.tree.selection()
        if not selected_item:
            return

        item_id = selected_item[0]
        row_values = self.alert_table.tree.item(item_id, "values")
        if not row_values or len(row_values) < 4:
            return

        time_str, threat_type, src_ip, raw_log = row_values[:4]
        decoded_log = urllib.parse.unquote(raw_log)

        remediation_db = {
            "SQL Injection": {
                "desc": "攻擊者企圖將惡意 SQL 語法注入到資料庫查詢中，可能導致資料庫洩漏、資料遭篡改或取得最高權限。",
                "risk": "高危 (High)",
                "remediation": [
                    "1. 使用參數化查詢 (Parameterized Queries) 或 Prepared Statements。",
                    "2. 避免直接以字串拼接建立 SQL 語法。",
                    "3. 實施嚴格的輸入驗證與過濾 (Input Sanitization)。",
                    "4. 對資料庫帳號落實最小權限原則 (Least Privilege)。"
                ]
            },
            "Cross-Site Scripting (XSS)": {
                "desc": "攻擊者嘗試將惡意 JavaScript 程式碼注入頁面，當其他使用者存取時執行，可能導致 Cookie/Session 竊取與帳號劫持。",
                "risk": "中高危 (Medium-High)",
                "remediation": [
                    "1. 對所有使用者輸入進行 HTML 實體編碼 (HTML Entity Encoding)。",
                    "2. 設定 Content Security Policy (CSP) 限制腳本執行。",
                    "3. 設定 Session Cookie 為 HttpOnly 屬性，防止腳本讀取。",
                    "4. 使用前端框架 (如 React, Vue) 自動轉義機制。"
                ]
            },
            "Path Traversal": {
                "desc": "攻擊者利用 ../ 等相對路徑符號企圖存取 Web 目錄以外的敏感檔案 (如 /etc/passwd 或系統設定檔)。",
                "risk": "高危 (High)",
                "remediation": [
                    "1. 禁止直接傳遞檔名或路徑作為參數。",
                    "2. 採用白名單 (Whitelist) 驗證允許存取的檔案列表。",
                    "3. 使用真實路徑檢查 (如 realpath) 並確保在 Root 目錄內。",
                    "4. 限制 Web 伺服器進程的檔案讀取權限。"
                ]
            },
            "Scanner Detected": {
                "desc": "偵測到自動化弱點掃描器 (如 Nmap, Nikto 等) 的 User-Agent 或特徵請求，通常為攻擊前的情報收集階段。",
                "risk": "中危 (Medium)",
                "remediation": [
                    "1. 在 WAF / 防火牆設定速率限制 (Rate Limiting) 與 IP 封鎖。",
                    "2. 隱藏 Web 伺服器版本資訊 (如 Server Header)。",
                    "3. 關閉不必要的目錄瀏覽與測試頁面。"
                ]
            }
        }

        detail = remediation_db.get(threat_type, {
            "desc": "偵測到可疑的 HTTP 存取行為，可能包含潛在安全風險。",
            "risk": "低中危 (Low-Medium)",
            "remediation": ["1. 檢查請求來源 IP 是否合法。", "2. 檢視 Web 伺服器應用程式日誌。"]
        })

        dialog = tk.Toplevel(self.root)
        dialog.title(f"SOC 事件應變分析 - [{threat_type}]")
        dialog.geometry("700x520")
        dialog.configure(bg="#121212")
        dialog.transient(self.root)
        dialog.grab_set()

        header_lbl = tk.Label(dialog, text=f"🚨 威脅分析詳情：{threat_type}", font=(config.FONT_FAMILY, 14, "bold"), bg="#222222", fg="#FF3333", pady=8)
        header_lbl.pack(fill=tk.X)

        content_frame = tk.Frame(dialog, bg="#121212", padx=15, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)

        info_text = f"• 發生時間:  {time_str}\n• 來源 IP:    {src_ip}\n• 風險等級:  {detail['risk']}"
        tk.Label(content_frame, text=info_text, font=("Consolas", 10), bg="#121212", fg="#00FF88", justify=tk.LEFT).pack(anchor="w", pady=(0, 10))

        desc_box = tk.LabelFrame(content_frame, text=" 威脅原理簡述 ", font=(config.FONT_FAMILY, 9, "bold"), bg="#121212", fg="#CCCCCC", padx=10, pady=5)
        desc_box.pack(fill=tk.X, pady=5)
        tk.Label(desc_box, text=detail['desc'], font=(config.FONT_FAMILY, 9), bg="#121212", fg="#DDDDDD", wraplength=640, justify=tk.LEFT).pack(anchor="w")

        payload_box = tk.LabelFrame(content_frame, text=" 攻擊 Payload (URL Decoded) ", font=(config.FONT_FAMILY, 9, "bold"), bg="#121212", fg="#CCCCCC", padx=10, pady=5)
        payload_box.pack(fill=tk.X, pady=5)
        payload_txt = tk.Text(payload_box, height=3, bg="#1E1E1E", fg="#FF8888", font=("Consolas", 9), relief="flat", wrap=tk.WORD)
        payload_txt.insert(tk.END, decoded_log)
        payload_txt.configure(state="disabled")
        payload_txt.pack(fill=tk.X)

        remediation_box = tk.LabelFrame(content_frame, text=" 🛡️ 專家建議防禦措施 (Remediation) ", font=(config.FONT_FAMILY, 9, "bold"), bg="#121212", fg="#00E5FF", padx=10, pady=5)
        remediation_box.pack(fill=tk.BOTH, expand=True, pady=5)
        
        rem_text = "\n".join(detail['remediation'])
        tk.Label(remediation_box, text=rem_text, font=(config.FONT_FAMILY, 9), bg="#121212", fg="#FFFFFF", justify=tk.LEFT, anchor="nw").pack(fill=tk.BOTH, expand=True)

        close_btn = tk.Button(dialog, text="關閉 (Esc)", command=dialog.destroy, bg="#333333", fg="#FFFFFF", font=(config.FONT_FAMILY, 9, "bold"), relief="flat", padx=15, pady=5)
        close_btn.pack(pady=8)
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def apply_filter(self, *args):
        try:
            selected_type, keyword = self.filter_bar.get_filter_criteria()
        except Exception:
            return

        keyword = keyword.strip().lower() if keyword else ""
        selected_type = selected_type.strip().lower() if selected_type else ""

        sorted_items = sorted(
            self.alert_items.items(),
            key=lambda x: x[1].get("time", ""),
            reverse=True
        )

        visible_count = 0
        total_count = len(self.all_alerts)

        for index, (item_id, alert_data) in enumerate(sorted_items):
            threat_type = alert_data.get("type", "")
            ip_addr = alert_data.get("ip", "")
            http_log = alert_data.get("log", "")

            match_keyword = (
                not keyword 
                or keyword in ip_addr 
                or keyword in http_log 
                or keyword in threat_type
            )
            
            match_type = (
                not selected_type
                or "全部" in selected_type 
                or "all" in selected_type
                or selected_type in threat_type 
                or threat_type in selected_type
                or ("xss" in selected_type and "xss" in threat_type)
                or ("sql" in selected_type and "sql" in threat_type)
                or ("path" in selected_type and "path" in threat_type)
                or ("scan" in selected_type and "scan" in threat_type)
            )

            if match_keyword and match_type:
                self.alert_table.tree.reattach(item_id, '', index)
                visible_count += 1
            else:
                self.alert_table.tree.detach(item_id)

        self.filter_bar.update_count(visible_count, total_count)

    def export_to_csv(self):
        visible_item_ids = self.alert_table.tree.get_children()

        if not visible_item_ids:
            messagebox.showwarning("匯出提示", "目前沒有可匯出的紀錄！")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 檔案", "*.csv"), ("所有檔案", "*.*")],
            title="儲存威脅紀錄匯出檔"
        )

        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["時間", "威脅類型", "來源 IP", "HTTP 存取紀錄 (URL Decoded)"])

                for item_id in visible_item_ids:
                    row_values = self.alert_table.tree.item(item_id, "values")
                    writer.writerow(row_values)

            messagebox.showinfo("匯出成功", f"已成功匯出 {len(visible_item_ids)} 筆威脅紀錄至：\n{file_path}")
        except Exception as e:
            messagebox.showerror("匯出失敗", f"寫入檔案時發生錯誤：\n{e}")

    def on_closing(self):
        try:
            if hasattr(self, 'monitor') and self.monitor:
                self.monitor.stop()
        except Exception:
            pass
        self.root.destroy()