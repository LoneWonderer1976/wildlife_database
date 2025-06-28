import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from ..database import init_db  # Relative import
from ..ui_components import setup_styles  # Relative import

def add_organism_type_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="Card.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Manage Organism Types", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)

    # Fetch existing organism types
    conn = sqlite3.connect("wildlife.db")
    c = conn.cursor()
    c.execute("SELECT type_id, type_name FROM organism_types")
    types = c.fetchall()
    c.execute("SELECT subtype_id, type_id, subtype_name FROM subtypes")
    subtypes = c.fetchall()
    conn.close()

    # Add new organism type
    ttk.Label(main_frame, text="New Type Name:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    new_type_name = ttk.Entry(main_frame)
    new_type_name.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    def save_new_type():
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO organism_types (type_name) VALUES (?)", (new_type_name.get(),))
            conn.commit()
            messagebox.showinfo("Success", "Organism type added")
            add_organism_type_page(app)  # Refresh page
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Type name must be unique")
        finally:
            conn.close()

    # Edit or delete existing type
    ttk.Label(main_frame, text="Select Type to Edit/Delete:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
    type_var = tk.StringVar()
    type_combobox = ttk.Combobox(main_frame, textvariable=type_var, values=[t[1] for t in types], state="readonly")
    type_combobox.grid(row=2, column=1, sticky="w", padx=10, pady=5)
    ttk.Label(main_frame, text="Edit Type Name:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
    edit_type_name = ttk.Entry(main_frame)
    edit_type_name.grid(row=3, column=1, sticky="w", padx=10, pady=5)

    def populate_edit_field(*args):
        selected_type = type_var.get()
        if selected_type:
            edit_type_name.delete(0, tk.END)
            edit_type_name.insert(0, selected_type)
            update_subtypes_display()

    type_var.trace("w", populate_edit_field)

    def edit_type():
        selected_type = type_var.get()
        new_name = edit_type_name.get()
        if not selected_type or not new_name:
            messagebox.showerror("Error", "Please select a type and enter a new name")
            return
        type_id = [t[0] for t in types if t[1] == selected_type][0]
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        try:
            c.execute("UPDATE organism_types SET type_name = ? WHERE type_id = ?", (new_name, type_id))
            conn.commit()
            messagebox.showinfo("Success", "Organism type updated")
            add_organism_type_page(app)  # Refresh page
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Type name must be unique")
        finally:
            conn.close()

    def delete_type():
        selected_type = type_var.get()
        if not selected_type:
            messagebox.showerror("Error", "Please select a type to delete")
            return
        type_id = [t[0] for t in types if t[1] == selected_type][0]
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM organisms WHERE type_id = ?", (type_id,))
        org_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM page_types WHERE type_id = ?", (type_id,))
        page_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM subtypes WHERE type_id = ?", (type_id,))
        subtype_count = c.fetchone()[0]
        if org_count > 0 or page_count > 0 or subtype_count > 0:
            messagebox.showerror("Error", "Cannot delete type; it is referenced by organisms, pages, or subtypes")
            conn.close()
            return
        if messagebox.askyesno("Confirm Delete", f"Delete type '{selected_type}'?"):
            c.execute("DELETE FROM organism_types WHERE type_id = ?", (type_id,))
            conn.commit()
            messagebox.showinfo("Success", "Type deleted")
            add_organism_type_page(app)  # Refresh page
        conn.close()

    # Manage subtypes
    ttk.Separator(main_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
    ttk.Label(main_frame, text="Manage Subtypes", style="Header.TLabel").grid(row=5, column=0, columnspan=2, pady=10)

    subtypes_frame = ttk.Frame(main_frame, style="TFrame")
    subtypes_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
    subtypes_canvas = tk.Canvas(subtypes_frame, bg="#FFFFFF")
    subtypes_scroll = ttk.Scrollbar(subtypes_frame, orient="vertical", command=subtypes_canvas.yview)
    subtypes_inner = ttk.Frame(subtypes_canvas, style="TFrame")
    subtypes_inner.bind("<Configure>", lambda e: subtypes_canvas.configure(scrollregion=subtypes_canvas.bbox("all")))
    subtypes_canvas.create_window((0, 0), window=subtypes_inner, anchor="nw")
    subtypes_canvas.configure(yscrollcommand=subtypes_scroll.set)
    subtypes_canvas.pack(side="left", fill="both", expand=True, padx=10)
    subtypes_scroll.pack(side="right", fill="y")

    def update_subtypes_display():
        for widget in subtypes_inner.winfo_children():
            widget.destroy()
        selected_type = type_var.get()
        if not selected_type:
            ttk.Label(subtypes_inner, text="Select a type to view subtypes").pack(pady=10)
            return
        type_id = [t[0] for t in types if t[1] == selected_type][0]
        current_subtypes = [s for s in subtypes if s[1] == type_id]
        if not current_subtypes:
            ttk.Label(subtypes_inner, text="No subtypes").pack(pady=10)
        for subtype in current_subtypes:
            subtype_frame = ttk.Frame(subtypes_inner, style="Card.TFrame")
            subtype_frame.pack(fill="x", padx=5, pady=5)
            ttk.Label(subtype_frame, text=subtype[2]).pack(side="left", padx=10)
            ttk.Button(subtype_frame, text="Edit", command=lambda sid=subtype[0], sn=subtype[2]: edit_subtype(sid, sn)).pack(side="right", padx=5)
            ttk.Button(subtype_frame, text="Delete", command=lambda sid=subtype[0]: delete_subtype(sid)).pack(side="right", padx=5)

    ttk.Label(main_frame, text="New Subtype Name:").grid(row=7, column=0, sticky="e", padx=10, pady=5)
    new_subtype_name = ttk.Entry(main_frame)
    new_subtype_name.grid(row=7, column=1, sticky="w", padx=10, pady=5)

    def add_subtype():
        selected_type = type_var.get()
        subtype_name = new_subtype_name.get()
        if not selected_type or not subtype_name:
            messagebox.showerror("Error", "Please select a type and enter a subtype name")
            return
        type_id = [t[0] for t in types if t[1] == selected_type][0]
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO subtypes (type_id, subtype_name) VALUES (?, ?)", (type_id, subtype_name))
            conn.commit()
            messagebox.showinfo("Success", "Subtype added")
            add_organism_type_page(app)  # Refresh page
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Subtype name must be unique for this type")
        finally:
            conn.close()

    def edit_subtype(subtype_id, current_name):
        new_name = tk.simpledialog.askstring("Edit Subtype", "Enter new subtype name:", initialvalue=current_name)
        if new_name:
            selected_type = type_var.get()
            type_id = [t[0] for t in types if t[1] == selected_type][0]
            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            try:
                c.execute("UPDATE subtypes SET subtype_name = ? WHERE subtype_id = ? AND type_id = ?", (new_name, subtype_id, type_id))
                conn.commit()
                messagebox.showinfo("Success", "Subtype updated")
                add_organism_type_page(app)  # Refresh page
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Subtype name must be unique for this type")
            finally:
                conn.close()

    def delete_subtype(subtype_id):
        selected_type = type_var.get()
        type_id = [t[0] for t in types if t[1] == selected_type][0]
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM organisms WHERE subtype_id = ?", (subtype_id,))
        org_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM page_subtypes WHERE subtype_id = ?", (subtype_id,))
        page_count = c.fetchone()[0]
        if org_count > 0 or page_count > 0:
            messagebox.showerror("Error", "Cannot delete subtype; it is referenced by organisms or pages")
            conn.close()
            return
        if messagebox.askyesno("Confirm Delete", "Delete this subtype?"):
            c.execute("DELETE FROM subtypes WHERE subtype_id = ? AND type_id = ?", (subtype_id, type_id))
            conn.commit()
            messagebox.showinfo("Success", "Subtype deleted")
            add_organism_type_page(app)  # Refresh page
        conn.close()

    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.grid(row=8, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="Save New Type", command=save_new_type, style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Edit Type", command=edit_type, style="Primary.TButton").grid(row=0, column=1, padx=10)
    ttk.Button(button_frame, text="Delete Type", command=delete_type, style="Secondary.TButton").grid(row=0, column=2, padx=10)
    ttk.Button(button_frame, text="Add Subtype", command=add_subtype, style="Primary.TButton").grid(row=0, column=3, padx=10)
    ttk.Button(button_frame, text="Back", command=app.create_home_page, style="Secondary.TButton").grid(row=0, column=4, padx=10)