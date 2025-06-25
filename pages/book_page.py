import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, Listbox

def add_page_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="Card.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Add Book Page", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
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

    # Add new page
    ttk.Label(main_frame, text="Page Number:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    page_number = ttk.Entry(main_frame)
    page_number.grid(row=1, column=1, sticky="w", padx=10, pady=5)
    ttk.Label(main_frame, text="Number of Organisms:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
    num_organisms = ttk.Entry(main_frame)
    num_organisms.grid(row=2, column=1, sticky="w", padx=10, pady=5)
    ttk.Label(main_frame, text="Organism Types:").grid(row=3, column=0, sticky="ne", padx=10, pady=5)
    types_listbox = Listbox(main_frame, selectmode="multiple", height=5)
    types_listbox.grid(row=3, column=1, sticky="w", padx=10, pady=5)
    for type_id, type_name in types:
        types_listbox.insert(tk.END, type_name)
    ttk.Label(main_frame, text="Subtypes (select types first):").grid(row=4, column=0, sticky="ne", padx=10, pady=5)
    subtypes_listbox = Listbox(main_frame, selectmode="multiple", height=5)
    subtypes_listbox.grid(row=4, column=1, sticky="w", padx=10, pady=5)

    def update_subtypes(*args):
        selected_type_indices = types_listbox.curselection()
        selected_type_ids = [types[i][0] for i in selected_type_indices]
        subtypes_listbox.delete(0, tk.END)
        if selected_type_ids:
            for subtype in [s for s in subtypes if s[1] in selected_type_ids]:
                subtypes_listbox.insert(tk.END, f"{[t[1] for t in types if t[0] == subtype[1]][0]}: {subtype[2]}")
        else:
            subtypes_listbox.insert(tk.END, "Select types to see subtypes")

    types_listbox.bind('<<ListboxSelect>>', update_subtypes)

    def save_page():
        try:
            page_num = int(page_number.get())
            num_orgs = int(num_organisms.get() or 0)
            selected_types = [types[i] for i in types_listbox.curselection()]
            selected_subtypes = [subtypes[i] for i in subtypes_listbox.curselection() if subtypes_listbox.get(i) != "Select types to see subtypes"]
            if not selected_types:
                messagebox.showerror("Error", "Please select at least one organism type")
                return
            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO book_pages (page_number, num_organisms) VALUES (?, ?)", (page_num, num_orgs))
                page_id = c.lastrowid
                for type_id, _ in selected_types:
                    c.execute("INSERT INTO page_types (page_id, type_id) VALUES (?, ?)", (page_id, type_id))
                for subtype_id, type_id, _ in selected_subtypes:
                    if type_id in [t[0] for t in selected_types]:
                        c.execute("INSERT INTO page_subtypes (page_id, subtype_id) VALUES (?, ?)", (page_id, subtype_id))
                conn.commit()
                messagebox.showinfo("Success", "Book page added")
                app.create_home_page()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Page number must be unique")
            finally:
                conn.close()
        except ValueError:
            messagebox.showerror("Error", "Page number and number of organisms must be numbers")

    # Edit or delete existing page
    ttk.Label(main_frame, text="Select Page to Edit/Delete:").grid(row=5, column=0, sticky="e", padx=10, pady=5)
    page_var = tk.StringVar()
    page_combobox = ttk.Combobox(main_frame, textvariable=page_var, values=[str(p[1]) for p in pages], state="readonly")
    page_combobox.grid(row=5, column=1, sticky="w", padx=10, pady=5)
    ttk.Label(main_frame, text="Edit Page Number:").grid(row=6, column=0, sticky="e", padx=10, pady=5)
    edit_page_number = ttk.Entry(main_frame)
    edit_page_number.grid(row=6, column=1, sticky="w", padx=10, pady=5)
    ttk.Label(main_frame, text="Edit Number of Organisms:").grid(row=7, column=0, sticky="e", padx=10, pady=5)
    edit_num_organisms = ttk.Entry(main_frame)
    edit_num_organisms.grid(row=7, column=1, sticky="w", padx=10, pady=5)
    ttk.Label(main_frame, text="Edit Organism Types:").grid(row=8, column=0, sticky="ne", padx=10, pady=5)
    edit_types_listbox = Listbox(main_frame, selectmode="multiple", height=5)
    edit_types_listbox.grid(row=8, column=1, sticky="w", padx=10, pady=5)
    for type_id, type_name in types:
        edit_types_listbox.insert(tk.END, type_name)
    ttk.Label(main_frame, text="Edit Subtypes:").grid(row=9, column=0, sticky="ne", padx=10, pady=5)
    edit_subtypes_listbox = Listbox(main_frame, selectmode="multiple", height=5)
    edit_subtypes_listbox.grid(row=9, column=1, sticky="w", padx=10, pady=5)

    def populate_edit_fields(*args):
        selected_page = page_var.get()
        if selected_page:
            page_id = [p[0] for p in pages if str(p[1]) == selected_page][0]
            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            c.execute("SELECT page_number, num_organisms FROM book_pages WHERE page_id = ?", (page_id,))
            page_data = c.fetchone()
            c.execute("SELECT type_id FROM page_types WHERE page_id = ?", (page_id,))
            selected_type_ids = [t[0] for t in c.fetchall()]
            c.execute("SELECT subtype_id FROM page_subtypes WHERE page_id = ?", (page_id,))
            selected_subtype_ids = [s[0] for s in c.fetchall()]
            conn.close()
            edit_page_number.delete(0, tk.END)
            edit_page_number.insert(0, page_data[0])
            edit_num_organisms.delete(0, tk.END)
            edit_num_organisms.insert(0, page_data[1] or "")
            edit_types_listbox.selection_clear(0, tk.END)
            for i, (type_id, _) in enumerate(types):
                if type_id in selected_type_ids:
                    edit_types_listbox.selection_set(i)
            edit_subtypes_listbox.delete(0, tk.END)
            selected_type_ids = [types[i][0] for i in edit_types_listbox.curselection()]
            if selected_type_ids:
                for subtype in [s for s in subtypes if s[1] in selected_type_ids]:
                    subtype_name = f"{[t[1] for t in types if t[0] == subtype[1]][0]}: {subtype[2]}"
                    edit_subtypes_listbox.insert(tk.END, subtype_name)
                    if subtype[0] in selected_subtype_ids:
                        edit_subtypes_listbox.selection_set(edit_subtypes_listbox.size() - 1)
            else:
                edit_subtypes_listbox.insert(tk.END, "Select types to see subtypes")

    page_var.trace("w", populate_edit_fields)
    edit_types_listbox.bind('<<ListboxSelect>>', lambda e: populate_edit_fields())

    def edit_page():
        selected_page = page_var.get()
        if not selected_page:
            messagebox.showerror("Error", "Please select a page to edit")
            return
        try:
            new_page_num = int(edit_page_number.get())
            new_num_orgs = int(edit_num_organisms.get() or 0)
            selected_types = [types[i] for i in edit_types_listbox.curselection()]
            selected_subtypes = [subtypes[i] for i in edit_subtypes_listbox.curselection() if edit_subtypes_listbox.get(i) != "Select types to see subtypes"]
            if not selected_types:
                messagebox.showerror("Error", "Please select at least one organism type")
                return
            page_id = [p[0] for p in pages if str(p[1]) == selected_page][0]
            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            try:
                c.execute("UPDATE book_pages SET page_number = ?, num_organisms = ? WHERE page_id = ?", (new_page_num, new_num_orgs, page_id))
                c.execute("DELETE FROM page_types WHERE page_id = ?", (page_id,))
                c.execute("DELETE FROM page_subtypes WHERE page_id = ?", (page_id,))
                for type_id, _ in selected_types:
                    c.execute("INSERT INTO page_types (page_id, type_id) VALUES (?, ?)", (page_id, type_id))
                for subtype_id, type_id, _ in selected_subtypes:
                    if type_id in [t[0] for t in selected_types]:
                        c.execute("INSERT INTO page_subtypes (page_id, subtype_id) VALUES (?, ?)", (page_id, subtype_id))
                conn.commit()
                messagebox.showinfo("Success", "Book page updated")
                add_page_page(app)  # Refresh page
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Page number must be unique")
            finally:
                conn.close()
        except ValueError:
            messagebox.showerror("Error", "Page number and number of organisms must be numbers")

    def delete_page():
        selected_page = page_var.get()
        if not selected_page:
            messagebox.showerror("Error", "Please select a page to delete")
            return
        page_id = [p[0] for p in pages if str(p[1]) == selected_page][0]
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM organisms WHERE book_page = ?", (int(selected_page),))
        org_count = c.fetchone()[0]
        if org_count > 0:
            messagebox.showerror("Error", "Cannot delete page with organisms")
            conn.close()
            return
        if messagebox.askyesno("Confirm Delete", f"Delete page {selected_page}?"):
            c.execute("DELETE FROM page_subtypes WHERE page_id = ?", (page_id,))
            c.execute("DELETE FROM page_types WHERE page_id = ?", (page_id,))
            c.execute("DELETE FROM book_pages WHERE page_id = ?", (page_id,))
            conn.commit()
            messagebox.showinfo("Success", "Book page deleted")
            add_page_page(app)  # Refresh page
        conn.close()

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=10, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="Save", command=save_page, style="Primary.TButton").grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Edit", command=edit_page, style="Primary.TButton").grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=delete_page, style="Secondary.TButton").grid(row=0, column=2, padx=5)
    ttk.Button(button_frame, text="Back", command=app.create_home_page, style="Secondary.TButton").grid(row=0, column=3, padx=5)