import os
import sys
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

APP_VERSION = "1.9"
TOOL_NAME = f"BlueFalcon NTK v{APP_VERSION}"

# ==========================================
# MATERIAL DESIGN 3 DARK THEME PALETTE
# ==========================================
MD_BG = "#131314"          
MD_SURFACE = "#1E1F20"     
MD_SURFACE_2 = "#282A2C"   
MD_SURFACE_3 = "#333538"   
MD_PRIMARY = "#8AB4F8"     
MD_ON_PRIMARY = "#000000"  
MD_TEXT = "#E3E3E3"        
MD_TEXT_MUTED = "#9AA0A6"  

MD_GREEN = "#81C995"       
MD_RED = "#F28B82"         
MD_YELLOW = "#FDE293"      
MD_CYAN = "#78D9EC"        

MD_NAV_ACTIVE_BG = "#C2E7FF"
MD_NAV_ACTIVE_FG = "#001D35"

def get_resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except AttributeError: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ScrollableTable(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=MD_SURFACE_2, corner_radius=24, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview", background=MD_SURFACE_2, foreground=MD_TEXT, fieldbackground=MD_SURFACE_2, rowheight=40, borderwidth=0, font=("Segoe UI", 11))
        style.map('Treeview', background=[('selected', MD_SURFACE_3)])
        
        style.configure("Treeview.Heading", background=MD_SURFACE, foreground=MD_TEXT_MUTED, font=("Segoe UI", 11, "bold"), borderwidth=0)
        style.map("Treeview.Heading", background=[('active', MD_SURFACE_3)])

        self.tree = ttk.Treeview(self, show="headings", selectmode="browse")
        
        self.tree.tag_configure('row_success', foreground=MD_GREEN)
        self.tree.tag_configure('row_warning', foreground=MD_YELLOW)
        self.tree.tag_configure('row_error', foreground=MD_RED)
        self.tree.tag_configure('row_neutral', foreground=MD_TEXT)
        self.tree.tag_configure('row_cyan', foreground=MD_CYAN)

        self.vsb = ctk.CTkScrollbar(self, orientation="vertical", command=self.tree.yview, fg_color="transparent", button_color=MD_SURFACE_3, button_hover_color=MD_PRIMARY)
        self.hsb = ctk.CTkScrollbar(self, orientation="horizontal", command=self.tree.xview, fg_color="transparent", button_color=MD_SURFACE_3, button_hover_color=MD_PRIMARY)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(20, 5), pady=(20, 5))
        self.vsb.grid(row=0, column=1, sticky="ns", padx=(0, 20), pady=(20, 5))
        self.hsb.grid(row=1, column=0, sticky="ew", padx=(20, 5), pady=(0, 20))
