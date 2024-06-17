import customtkinter as ctk
import tkinter as tk
import settings as st
import host
import viewer
import threading
import sys

def open_movieM_Host(menu):
    menu.destroy()
    host.open_movieM_Host()

def open_movieM_Viewer(menu):
    menu.destroy()
    viewer.open_movieM_Viewer()

def on_closing():
    # Implement any cleanup actions here, like stopping threads
    print("Closing application...")
    sys.exit(0)

def open_movieM_Menu():
    ctk.set_appearance_mode(st.default_appearance_mode)
    ctk.set_default_color_theme(st.default_color_theme)

    menu = ctk.CTk()
    menu.geometry("680x430")
    menu.minsize(680, 430)

    # Handle window close event
    menu.protocol("WM_DELETE_WINDOW", on_closing)

    button_H = ctk.CTkButton(master=menu, text="Host Room", corner_radius=30, command=lambda: open_movieM_Host(menu),
                             height=240, width=240, font=(st.default_font_family, st.font_sizes["large"]))
    button_H.place(relx=0.25, rely=0.5, anchor=ctk.CENTER)

    button_J = ctk.CTkButton(master=menu, text="Join Room", corner_radius=30, command=lambda: open_movieM_Viewer(menu),
                             height=240, width=240, font=(st.default_font_family, st.font_sizes["large"]))
    button_J.place(relx=0.75, rely=0.5, anchor=ctk.CENTER)

    menu.mainloop()

if __name__ == '__main__':
    open_movieM_Menu()
