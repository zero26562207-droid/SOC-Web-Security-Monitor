import time
import paramiko
import config
from core.log_parser import LogParser

class SSHLogMonitor:
    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        self.is_running = True

    def start_polling(self):
        """背景執行 SSH Polling 任務"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # 移除不相容的 disabled_algorithms 參數
            ssh.connect(
                config.VM_IP, 
                port=config.PORT, 
                username=config.USERNAME, 
                password=config.PASSWORD, 
                timeout=10
            )
            sftp = ssh.open_sftp()
            
            self.msg_queue.put(("STATUS", ("運行正常 (Polling 中...)", 0)))
            last_line_count = 0

            while self.is_running:
                try:
                    with sftp.open(config.REMOTE_LOG_PATH, 'r') as f:
                        lines = f.readlines()
                        current_line_count = len(lines)

                        if current_line_count > last_line_count:
                            new_lines = lines[last_line_count:]
                            last_line_count = current_line_count

                            for line in new_lines:
                                alert = LogParser.parse_line(line)
                                if alert:
                                    self.msg_queue.put(("ALERT", alert))

                        self.msg_queue.put(("STATUS", ("運行正常 (Polling 中...)", current_line_count)))

                except Exception as read_err:
                    self.msg_queue.put(("STATUS", (f"讀取異常: {read_err}", 0)))

                time.sleep(3)

            sftp.close()
            ssh.close()

        except Exception as e:
            self.msg_queue.put(("STATUS", (f"連線失敗: {e}", 0)))

    def stop(self):
        self.is_running = False