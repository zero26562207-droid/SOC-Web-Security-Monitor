import json
import os

SETTINGS_FILE = "settings.json"

# 預設連線設定
DEFAULT_CONFIG = {
    "SSH_HOST": "192.168.56.102",
    "SSH_PORT": 22,
    "SSH_USER": "msfadmin",
    "SSH_PASS": "msfadmin",
    "LOG_PATH": "/var/log/apache2/access.log"
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 初始載入連線資訊
current_config = load_settings()

# 🔗 變數全名與別名整合 (防止連線模組找不到變數)
SSH_HOST = HOST = IP = VM_IP = current_config.get("SSH_HOST", "192.168.56.102")
SSH_PORT = PORT = VM_PORT = int(current_config.get("SSH_PORT", 22))
SSH_USER = USER = USERNAME = VM_USER = current_config.get("SSH_USER", "msfadmin")
SSH_PASS = PASS = PASSWORD = VM_PASS = current_config.get("SSH_PASS", "msfadmin")
LOG_PATH = REMOTE_LOG_PATH = current_config.get("LOG_PATH", "/var/log/apache2/access.log")

# 🎨 SOC UI 主題與顏色設定
THEME_BG = "#181818"          # 全域主要背景色
THEME_PANEL_BG = "#222222"    # 過濾區塊 / 面板背景色

COLOR_PRIMARY = "#00FF88"     # 主標題 / 亮綠色
COLOR_WARN = "#FFCC00"        # 警告黃色
COLOR_DANGER = "#FF3333"      # 高危紅色
COLOR_BG = "#121212"          # 深黑背景色
COLOR_TEXT = "#FFFFFF"        # 一般文字白色
COLOR_ALERT = "#FF3333"       # 告警文字紅色

FONT_FAMILY = "Microsoft JhengHei"  # 微軟正黑體