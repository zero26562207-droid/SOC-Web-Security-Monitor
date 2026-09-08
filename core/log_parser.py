import time
from urllib.parse import unquote
from core.threat_rules import SECURITY_RULES

class LogParser:
    @staticmethod
    def parse_line(line: str):
        """解碼單行日誌並比對威脅特徵"""
        decoded_line = unquote(line)
        parts = line.split()
        source_ip = parts[0] if len(parts) > 0 else "UNKNOWN"

        for threat_name, pattern in SECURITY_RULES.items():
            if pattern.search(decoded_line):
                timestamp = time.strftime('%H:%M:%S', time.localtime())
                return {
                    "time": timestamp,
                    "threat": threat_name,
                    "ip": source_ip,
                    "request": decoded_line.strip()
                }
        return None