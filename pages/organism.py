import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

def add_organism_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="Card.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Add Organism", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
    conn = sqlite3.connect("wildlife.db")
    c = conn.cursor()
    c.execute("SELECT type_id, type_name FROM organism_types")
    types = c.fetchall()
    c.execute("SELECT subtype_id, type_id, subtype_name FROM subtypes")
    subtypes = c.fetchall()
    c.execute("SELECT page_id, page_number FROM book_pages")
    pages = c.fetchall()
    c.execute("SELECT page_id, type_id FROM page_types")
    page_types = c.fetchall()
    c.execute("SELECT page_id, subtype_id FROM page_subtypes")
    page_subtypes = c.fetchall()
    conn.close()

    fields = [
        ("Organism Type:", ttk.Combobox(main_frame, values=[t[1] for t in types], state="readonly")),
        ("Subtype:", ttk.Combobox(main_frame, state="readonly")),
        ("Name:", ttk.Entry(main_frame)),
        ("Genus:", ttk.Entry(main_frame)),
        ("Species:", ttk.Entry(main_frame)),
        ("Book Page:", ttk.Combobox(main_frame, values=[str(p[1]) for p in pages], state="readonly")),
        ("Page Position:", ttk.Entry(main_frame))
    ]
    for i, (label, widget) in enumerate(fields, 1):
        ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=5)
        widget.grid(row=i, column=1, sticky="w", padx=10, pady=5)
    type_var = fields[0][1]
    subtype_var = fields[1][1]
    page_var = fields[5][1]

    def update_subtypes(*args):
        subtype_var.set("")
        subtype_combobox = fields[1][1]
        selected_type = type_var.get()
        selected_page = page_var.get()
        allowed_subtype_ids = []
        if selected_page:
            page_id = [p[0] for p in pages if str(p[1]) == selected_page][0]
            allowed_subtype_ids = [ps[1] for ps in page_subtypes if ps[0] == page_id]
        if selected_type:
            type_id = [t[0] for t in types if t[1] == selected_type][0]
            subtype_values = [s[2] for s in subtypes if s[1] == type_id]
            if allowed_subtype_ids:
                subtype_values = [s[2] for s in subtypes if s[1] == type_id and s[0] in allowed_subtype_ids]
            subtype_combobox['values'] = subtype_values
        else:
            subtype_combobox['values'] = []

    type_var.trace("w", update_subtypes)
    page_var.trace("w", update_subtypes)

    def save_organism():
        selected_type = type_var.get()
        selected_subtype = subtype_var.get()
        selected_page = page_var.get()
        type_id = [t[0] for t in types if t[1] == selected_type][0] if selected_type else None
        subtype_id = [s[0] for s in subtypes if s[2] == selected_subtype and s[1] == type_id][0] if selected_subtype and type_id else None
        if selected_page and type_id:
            page_id = [p[0] for p in pages if str(p[1]) == selected_page][0]
            allowed_types = set(t[1] for t in page_types if t[0] == page_id)
            allowed_subtypes = set(s[1] for s in page_subtypes if s[0] == page_id)
            if type_id not in allowed_types:
                messagebox.showerror("Error", "Selected type is not associated with this page")
                return
            if subtype_id and subtype_id not in allowed_subtypes:
                messagebox.showerror("Error", "Selected subtype is not associated with this page")
                return
        try:
            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            c.execute("INSERT INTO organisms (type_id, subtype_id, name, genus, species, book_page, page_position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (type_id, subtype_id, fields[2][1].get(), fields[3][1].get(), fields[4][1].get(),
                       int(fields[5][1].get()) if selected_page else None,
                       int(fields[6][1].get() or 0)))
            conn.commit()
            messagebox.showinfo("Success", "Organism added")
            app.create_home_page()
        except ValueError:
            messagebox.showerror("Error", "Page position must be a number")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Invalid data or database constraint violated")
        finally:
            conn.close()

    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="Save", command=save_organism, style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Back", command=app.create_home_page, style="Secondary.TButton").grid(row=0, column=1, padx=10)