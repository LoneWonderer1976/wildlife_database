import tkinter as tk
from tkinter import ttk

def setup_styles(app):
    app.style = ttk.Style()
    app.style.configure("TFrame", background="#E6F0FA")
    app.style.configure("Card.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)
    app.style.configure("Primary.TButton", background="#D4EAD4", foreground="#333333", font=("Helvetica", 12),
                        padding=10)
    app.style.map("Primary.TButton", background=[("active", "#B8DAB8")])
    app.style.configure("Secondary.TButton", background="#FFE4D6", foreground="#333333", font=("Helvetica", 12),
                        padding=10)
    app.style.map("Secondary.TButton", background=[("active", "#FFD4C6")])
    app.style.configure("TLabel", background="#E6F0FA", foreground="#333333", font=("Helvetica", 12))
    app.style.configure("Header.TLabel", background="#E6F0FA", foreground="#333333", font=("Helvetica", 16, "bold"))
    app.style.configure("TCombobox", fieldbackground="#FFFFFF", foreground="#333333", font=("Helvetica", 12))
    app.style.configure("TEntry", fieldbackground="#FFFFFF", foreground="#333333", font=("Helvetica", 12))
    app.style.configure("TScrollbar", background="#E6E6FA", troughcolor="#E6F0FA")