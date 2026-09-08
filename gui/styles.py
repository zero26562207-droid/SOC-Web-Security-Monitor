from tkinter import ttk
import config

def apply_theme():
    """套用 SOC 專用的深色主題"""
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview",
                    background=config.THEME_ROW_BG,
                    foreground=config.COLOR_TEXT,
                    fieldbackground=config.THEME_ROW_BG,
                    rowheight=28,
                    font=(config.FONT_FAMILY, 10))
    style.configure("Treeview.Heading",
                    background="#3c3c3c",
                    foreground=config.COLOR_PRIMARY,
                    font=(config.FONT_FAMILY, 11, 'bold'))
    style.map("Treeview", background=[('selected', '#007acc')])