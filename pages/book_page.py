import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from ..database import init_db  # Relative import
from ..ui_components import setup_styles  # Relative import

def add_page_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="Card.TFrame", padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Manage Book Pages", style="Header.TLabel").grid(row=0, column=0, columnspan=3, pady=10)

    # Fetch data from database
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

    # --- Add New Page Section ---
    ttk.Label(main_frame, text="Add New Page", style="Header.TLabel").grid(row=1, column=0, columnspan=3, pady=10)
    add_frame = ttk.Frame(main_frame, style="TFrame")
    add_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10)

    ttk.Label(add_frame, text="Page Number:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
    page_number = ttk.Entry(add_frame)
    page_number.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(add_frame, text="Number of Organisms:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    num_organisms = ttk.Entry(add_frame)
    num_organisms.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(add_frame, text="Select Types/Subtypes:").grid(row=2, column=0, sticky="ne", padx=10, pady=5)
    tree = ttk.Treeview(add_frame, columns=("Name",), show="tree", height=8)
    tree.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
    tree_scroll = ttk.Scrollbar(add_frame, orient="vertical", command=tree.yview)
    tree_scroll.grid(row=2, column=2, sticky="ns", pady=5)
    tree.configure(yscrollcommand=tree_scroll.set)
    add_frame.grid_columnconfigure(1, weight=1)

    # Populate Treeview with types and subtypes
    type_dict = {t[0]: t[1] for t in types}
    subtype_dict = {s[0]: (s[1], s[2]) for s in subtypes}
    for type_id, type_name in types:
        parent = tree.insert("", "end", text=type_name, values=(type_name,), tags=("type", type_id))
        for subtype_id, subtype_data in subtype_dict.items():
            if subtype_data[0] == type_id:
                tree.insert(parent, "end", text=subtype_data[1], values=(subtype_data[1],), tags=("subtype", subtype_id))

    def save_page():
        try:
            page_num = int(page_number.get())
            num_orgs = int(num_organisms.get() or 0)
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showerror("Error", "Please select at least one type or subtype")
                return
            selected_types = set()
            selected_subtypes = set()
            for item in selected_items:
                tags = tree.item(item, "tags")
                item_type, item_id = tags[0], int(tags[1])
                if item_type == "type":
                    selected_types.add(item_id)
                else:
                    selected_subtypes.add(item_id)
                    type_id = subtype_dict[item_id][0]
                    selected_types.add(type_id)  # Ensure parent type is included

            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO book_pages (page_number, num_organisms) VALUES (?, ?)", (page_num, num_orgs))
                page_id = c.lastrowid
                for type_id in selected_types:
                    c.execute("INSERT INTO page_types (page_id, type_id) VALUES (?, ?)", (page_id, type_id))
                for subtype_id in selected_subtypes:
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

    ttk.Button(add_frame, text="Save New Page", command=save_page, style="Primary.TButton").grid(row=3, column=1, sticky="w", padx=10, pady=10)

    # --- Edit/Delete Page Section ---
    ttk.Separator(main_frame, orient="horizontal").grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")
    ttk.Label(main_frame, text="Edit or Delete Page", style="Header.TLabel").grid(row=4, column=0, columnspan=3, pady=10)
    edit_frame = ttk.Frame(main_frame, style="TFrame")
    edit_frame.grid(row=5, column=0, columnspan=3, sticky="ew", padx=10)

    ttk.Label(edit_frame, text="Select Page:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
    page_var = tk.StringVar()
    page_combobox = ttk.Combobox(edit_frame, textvariable=page_var, values=[str(p[1]) for p in pages], state="readonly")
    page_combobox.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(edit_frame, text="Edit Page Number:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    edit_page_number = ttk.Entry(edit_frame)
    edit_page_number.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(edit_frame, text="Edit Number of Organisms:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
    edit_num_organisms = ttk.Entry(edit_frame)
    edit_num_organisms.grid(row=2, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(edit_frame, text="Edit Types/Subtypes:").grid(row=3, column=0, sticky="ne", padx=10, pady=5)
    edit_tree = ttk.Treeview(edit_frame, columns=("Name",), show="tree", height=8)
    edit_tree.grid(row=3, column=1, sticky="nsew", padx=10, pady=5)
    edit_tree_scroll = ttk.Scrollbar(edit_frame, orient="vertical", command=edit_tree.yview)
    edit_tree_scroll.grid(row=3, column=2, sticky="ns", pady=5)
    edit_tree.configure(yscrollcommand=edit_tree_scroll.set)
    edit_frame.grid_columnconfigure(1, weight=1)

    def populate_edit_fields(*args):
        selected_page = page_var.get()
        if selected_page:
            page_id = [p[0] for p in pages if str(p[1]) == selected_page][0]
            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            c.execute("SELECT page_number, num_organisms FROM book_pages WHERE page_id = ?", (page_id,))
            page_data = c.fetchone()
            c.execute("SELECT type_id FROM page_types WHERE page_id = ?", (page_id,))
            selected_type_ids = set(t[0] for t in c.fetchall())
            c.execute("SELECT subtype_id FROM page_subtypes WHERE page_id = ?", (page_id,))
            selected_subtype_ids = set(s[0] for s in c.fetchall())
            conn.close()

            edit_page_number.delete(0, tk.END)
            edit_page_number.insert(0, page_data[0])
            edit_num_organisms.delete(0, tk.END)
            edit_num_organisms.insert(0, page_data[1] or "")

            # Populate Treeview
            edit_tree.delete(*edit_tree.get_children())
            for type_id, type_name in types:
                parent = edit_tree.insert("", "end", text=type_name, values=(type_name,), tags=("type", type_id))
                if type_id in selected_type_ids:
                    edit_tree.selection_add(parent)
                for subtype_id, subtype_data in subtype_dict.items():
                    if subtype_data[0] == type_id:
                        child = edit_tree.insert(parent, "end", text=subtype_data[1], values=(subtype_data[1],), tags=("subtype", subtype_id))
                        if subtype_id in selected_subtype_ids:
                            edit_tree.selection_add(child)

    page_var.trace("w", populate_edit_fields)

    def edit_page():
        selected_page = page_var.get()
        if not selected_page:
            messagebox.showerror("Error", "Please select a page to edit")
            return
        try:
            new_page_num = int(edit_page_number.get())
            new_num_orgs = int(edit_num_organisms.get() or 0)
            selected_items = edit_tree.selection()
            if not selected_items:
                messagebox.showerror("Error", "Please select at least one type or subtype")
                return
            selected_types = set()
            selected_subtypes = set()
            for item in selected_items:
                tags = edit_tree.item(item, "tags")
                item_type, item_id = tags[0], int(tags[1])
                if item_type == "type":
                    selected_types.add(item_id)
                else:
                    selected_subtypes.add(item_id)
                    type_id = subtype_dict[item_id][0]
                    selected_types.add(type_id)

            page_id = [p[0] for p in pages if str(p[1]) == selected_page][0]
            conn = sqlite3.connect("wildlife.db")
            c = conn.cursor()
            try:
                c.execute("UPDATE book_pages SET page_number = ?, num_organisms = ? WHERE page_id = ?", (new_page_num, new_num_orgs, page_id))
                c.execute("DELETE FROM page_types WHERE page_id = ?", (page_id,))
                c.execute("DELETE FROM page_subtypes WHERE page_id = ?", (page_id,))
                for type_id in selected_types:
                    c.execute("INSERT INTO page_types (page_id, type_id) VALUES (?, ?)", (page_id, type_id))
                for subtype_id in selected_subtypes:
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
            messagebox.showerror("Error", "Cannot delete page with associated organisms")
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

    ttk.Button(edit_frame, text="Edit Page", command=edit_page, style="Primary.TButton").grid(row=4, column=1, sticky="w", padx=10, pady=5)
    ttk.Button(edit_frame, text="Delete Page", command=delete_page, style="Secondary.TButton").grid(row=4, column=2, sticky="w", padx=10, pady=5)

    # Back Button
    ttk.Button(main_frame, text="Back", command=app.create_home_page, style="Secondary.TButton").grid(row=6, column=2, sticky="e", padx=10, pady=20)