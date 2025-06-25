import tkinter as tk
from tkinter import ttk

def create_home_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Wildlife Database", style="Header.TLabel").grid(row=0, column=0, pady=20)
    buttons = [
        ("Add an Organism", app.add_organism_page),
        ("Add a Page", app.add_page_page),
        ("Add an Organism Type", app.add_organism_type_page),
        ("Add a Photo", app.add_photo_page),
        ("Browse Photos", app.browse_options_page),
        ("Search Photos", app.search_photos_page)
    ]
    for i, (text, command) in enumerate(buttons, 1):
        ttk.Button(main_frame, text=text, command=command, style="Primary.TButton").grid(row=i, column=0, pady=10, sticky="ew")