\# 🛡️ SOC Web Security Monitoring GUI
![SOC Web Security Monitoring GUI](dashboard.png)



一個採用 Cyberpunk 暗黑視覺風格的桌面型 SOC（安全運營中心）Web 日誌即時監控與威脅分析系統。



\## 🌟 系統亮點

\- \*\*即時遠端日誌輪詢\*\*：透過 SSH (Paramiko) 背景抓取 Linux 靶機（Metasploitable2 / Kali）之 Apache `access.log`。

\- \*\*多重威脅特徵分析\*\*：即時比對 SQL 注入 (SQLi)、跨站腳本 (XSS)、路徑遍歷 (Path Traversal) 與漏洞掃描器。

\- \*\*非阻塞 UI 架構\*\*：採用 `threading` 與 `queue` 實現多執行緒傳輸，巨量 Log 刷新時介面依然流暢。

\- \*\*事件應變處置建議 (Incident Response)\*\*：雙擊告警事件即時彈出攻擊 Payload 解析與藍隊修補建議。

\- \*\*動態設定與報表匯出\*\*：支援 Runtime 動態修改連線資訊，並可一鍵匯出 CSV 告警報表。



\## 🛠️ 技術棧

\- \*\*Language\*\*: Python 3

\- \*\*GUI\*\*: Tkinter / ttk

\- \*\*SSH Protocol\*\*: Paramiko

\- \*\*Threat Engine\*\*: Regular Expressions (Regex)

\- \*\*Config \& Report\*\*: JSON, CSV



\## 🚀 快速開始



\### 1. 安裝依賴

```bash

pip install paramiko

