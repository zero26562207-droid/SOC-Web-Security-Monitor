import tkinter as tk
from gui.app import SOCAppGUI

def main():
    root = tk.Tk()
    
    # 強制將視窗跳至最前層
    root.attributes('-topmost', True)
    
    app = SOCAppGUI(root)
    
    # 顯示後取消強制置頂，避免影響其他視窗
    root.after(1000, lambda: root.attributes('-topmost', False))
    
    root.mainloop()

if __name__ == "__main__":
    main()