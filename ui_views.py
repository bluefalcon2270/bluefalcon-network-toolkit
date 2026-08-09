import os
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk

from config_manager import ConfigManager
from ui_shared import MD_BG, MD_SURFACE, MD_PRIMARY, MD_RED, MD_TEXT, MD_TEXT_MUTED, MD_SURFACE_2, APP_VERSION

class ViewBuilder:

    @staticmethod
    def build_profiles_view(app, parent_frame):
        frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        ctk.CTkLabel(frame, text="📁 Profile Manager", font=("Segoe UI", 24, "bold"), text_color=MD_TEXT).pack(anchor="w", pady=(20, 20), padx=30)

        edit_card = ctk.CTkFrame(frame, fg_color=MD_SURFACE, corner_radius=24)
        edit_card.pack(fill="both", expand=True, padx=30, pady=10)

        file_frame = ctk.CTkFrame(edit_card, fg_color="transparent")
        file_frame.pack(fill="x", padx=30, pady=(30, 10))

        target_editor = ctk.CTkTextbox(edit_card, font=("Consolas", 15), fg_color=MD_BG, text_color=MD_TEXT, corner_radius=16, border_width=1, border_color=MD_SURFACE_2)
        target_editor.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        undo_content = {"text": None}
        btn_undo = ctk.CTkButton(file_frame, text="Undo", width=70, height=40, corner_radius=20, fg_color=MD_RED, text_color="#000000", font=("Segoe UI", 13, "bold"))

        def load_current():
            target_editor.delete("1.0", "end")
            target_editor.insert("1.0", ConfigManager.load_profile_raw())
            
        load_current()

        def open_file():
            import os
            if not os.path.exists("Profile.txt"):
                ConfigManager.save_profile(ConfigManager.get_default())
            os.startfile(os.path.abspath("Profile.txt"))

        def load_template():
            undo_content["text"] = target_editor.get("1.0", "end")
            target_editor.delete("1.0", "end")
            target_editor.insert("1.0", ConfigManager.get_default())
            btn_undo.pack(side="left", padx=(10, 0))

        def undo_template():
            if undo_content["text"] is not None:
                target_editor.delete("1.0", "end")
                target_editor.insert("1.0", undo_content["text"])
                undo_content["text"] = None
                btn_undo.pack_forget()

        def save_targets():
            content = target_editor.get("1.0", "end").strip()
            formatted = ConfigManager.save_profile(content)
            target_editor.delete("1.0", "end")
            target_editor.insert("1.0", formatted)
            btn_undo.pack_forget()

        btn_browse = ctk.CTkButton(file_frame, text="Open Profile File", width=120, height=40, corner_radius=20, fg_color="#1F2937", text_color=MD_TEXT, hover_color="#374151", border_width=1, border_color="#374151", font=("Segoe UI", 13, "bold"), command=open_file)
        btn_browse.pack(side="left", padx=(0, 15))
        
        btn_template = ctk.CTkButton(file_frame, text="Reset to Default", width=120, height=40, corner_radius=20, fg_color="#1F2937", text_color=MD_TEXT, hover_color="#374151", border_width=1, border_color="#374151", font=("Segoe UI", 13, "bold"), command=load_template)
        btn_template.pack(side="left")

        btn_undo.configure(command=undo_template)
        
        btn_save = ctk.CTkButton(file_frame, text="Save & Format", font=("Segoe UI", 14, "bold"), height=40, corner_radius=20, fg_color=MD_PRIMARY, text_color="#000000", command=save_targets)
        btn_save.pack(side="right")

        return frame

    @staticmethod
    def build_about_view(app, parent_frame):
        frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        
        card = ctk.CTkFrame(frame, fg_color=MD_SURFACE, corner_radius=32, width=600, height=450)
        card.pack_propagate(False)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card, text="🦅", font=("Segoe UI Emoji", 64)).pack(pady=(50, 15))
        ctk.CTkLabel(card, text="Ultimate Network Toolkit", text_color=MD_TEXT, font=("Segoe UI", 28, "bold")).pack(pady=0)
        ctk.CTkLabel(card, text=f"Version {APP_VERSION}", text_color=MD_PRIMARY, font=("Segoe UI", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(card, text="A high-performance async diagnostic utility.", text_color=MD_TEXT_MUTED, font=("Segoe UI", 15)).pack(pady=(15, 5))
        ctk.CTkLabel(card, text="Developed with love by BlueFalcon", text_color=MD_TEXT_MUTED, font=("Segoe UI", 14, "italic")).pack(pady=(5, 40))
        
        links = ctk.CTkFrame(card, fg_color="transparent")
        links.pack(pady=10)
        
        btn_gh = ctk.CTkButton(links, text="GitHub", font=("Segoe UI", 15, "bold"), height=48, width=120, fg_color="#282A2C", hover_color="#383A3C", text_color=MD_TEXT, corner_radius=24, command=lambda: webbrowser.open_new_tab("https://github.com/bluefalcon2270/bluefalcon-ultimate-network-toolkit"))
        btn_gh.pack(side="left", padx=10)
        
        btn_email = ctk.CTkButton(links, text="BlueFalcon2270@gmail.com", font=("Segoe UI", 15, "bold"), height=48, fg_color=MD_BG, hover_color="#282A2C", text_color=MD_TEXT, corner_radius=24)
        
        def copy_email():
            app.clipboard_clear()
            app.clipboard_append("BlueFalcon2270@gmail.com")
            btn_email.configure(text="Copied to Clipboard!")
            app.after(2000, lambda: btn_email.configure(text="BlueFalcon2270@gmail.com"))
            
        btn_email.configure(command=copy_email)
        btn_email.pack(side="left", padx=10)

        return frame
