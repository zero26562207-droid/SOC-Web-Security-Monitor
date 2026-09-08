import re

# 威脅特徵庫
SECURITY_RULES = {
    "SQL Injection": re.compile(r"(union\s+select|select\s+.*?\s+from|' OR '1'='1|--|;\s*drop|%27%20OR)", re.IGNORECASE),
    "Cross-Site Scripting (XSS)": re.compile(r"(<script.*?>|javascript:|onload=|<img\s+src=)", re.IGNORECASE),
    "Path Traversal": re.compile(r"(\.\./\.\./|/etc/passwd|c:\\windows)", re.IGNORECASE),
    "Scanner Detected": re.compile(r"(nikto|OWASP|sqlmap|nmap)", re.IGNORECASE),
}