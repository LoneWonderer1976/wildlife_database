import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

def search_photos_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Search Photos", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
    conn = sqlite3.connect("wildlife.db")
    c = conn.cursor()
    c.execute("SELECT type_id, type_name FROM organism_types")
    types = c.fetchall()
    c.execute("SELECT subtype_id, type_id, subtype_name FROM subtypes")
    subtypes = c.fetchall()
    c.execute("SELECT ps.subject_id, ps.photo_id, o.name, ps.subject_rating, ps.subject_sex, ps.is_juvenile, ps.is_flying, ps.has_flowers, ps.has_leaves, ps.has_trunk_stem, ps.has_fruit, ps.notes FROM photo_subjects ps LEFT JOIN organisms o ON ps.organism_id = o.organism_id")
    subjects = c.fetchall()
    conn.close()

    fields = [
        ("Organism Name:", ttk.Entry(main_frame)),
        ("Organism Type:", ttk.Combobox(main_frame, values=[t[1] for t in types], state="readonly")),
        ("Subtype:", ttk.Combobox(main_frame, state="readonly")),
        ("Page Number:", ttk.Entry(main_frame)),
        ("Date Taken:", ttk.Entry(main_frame)),
        ("Location:", ttk.Entry(main_frame))
    ]
    for i, (label, widget) in enumerate(fields, 1):
        ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=5)
        widget.grid(row=i, column=1, sticky="w", padx=10, pady=5)
    type_var = fields[1][1]
    subtype_var = fields[2][1]

    def update_subtypes(*args):
        subtype_var.set("")
        subtype_combobox = fields[2][1]
        selected_type = type_var.get()
        if selected_type:
            type_id = [t[0] for t in types if t[1] == selected_type][0]
            subtype_combobox['values'] = [s[2] for s in subtypes if s[1] == type_id]
        else:
            subtype_combobox['values'] = []

    type_var.trace("w", update_subtypes)

    results_frame = ttk.Frame(main_frame, style="TFrame")
    results_frame.grid(row=len(fields)+2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    main_frame.grid_rowconfigure(len(fields)+2, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    canvas = tk.Canvas(results_frame, bg="#E6F0FA")
    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="TFrame")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=1160)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    results_frame.grid_columnconfigure(0, weight=1)
    results_frame.grid_rowconfigure(0, weight=1)

    def search():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        query = """
            SELECT DISTINCT p.photo_id, p.file_path, p.date_taken, p.location, p.lat_degrees, p.lat_minutes, p.lon_degrees, p.lon_minutes, p.rating
            FROM photos p
            LEFT JOIN photo_subjects ps ON p.photo_id = ps.photo_id
            LEFT JOIN organisms o ON ps.organism_id = o.organism_id
            LEFT JOIN organism_types ot ON o.type_id = ot.type_id
            LEFT JOIN subtypes st ON o.subtype_id = st.subtype_id
            LEFT JOIN book_pages b ON o.book_page = b.page_number
            LEFT JOIN page_types pt ON b.page_id = pt.page_id
            LEFT JOIN page_subtypes psu ON b.page_id = psu.page_id
            WHERE 1=1
        """
        params = []
        if fields[0][1].get():
            query += " AND o.name LIKE ?"
            params.append(f"%{fields[0][1].get()}%")
        if fields[1][1].get():
            query += " AND ot.type_name = ?"
            params.append(fields[1][1].get())
        if fields[2][1].get():
            query += " AND (st.subtype_name = ? OR psu.subtype_id = (SELECT subtype_id FROM subtypes WHERE subtype_name = ? AND type_id = ot.type_id))"
            params.append(fields[2][1].get())
            params.append(fields[2][1].get())
        if fields[3][1].get():
            query += " AND b.page_number = ?"
            params.append(int(fields[3][1].get()))
        if fields[4][1].get():
            query += " AND p.date_taken LIKE ?"
            params.append(f"%{fields[4][1].get()}%")
        if fields[5][1].get():
            query += " AND p.location LIKE ?"
            params.append(f"%{fields[5][1].get()}%")
        c.execute(query, params)
        results = c.fetchall()
        conn.close()

        if not results:
            ttk.Label(scrollable_frame, text="No results").pack(pady=10, fill="x")
            return

        for r in results:
            photo_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
            photo_frame.pack(fill="x", padx=5, pady=5)
            try:
                img = Image.open(r[1])
                img.thumbnail((300, 300))
                photo_img = ImageTk.PhotoImage(img)
                image_label = ttk.Label(photo_frame, image=photo_img)
                image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
                image_label.image = photo_img
                image_label.bind("<Button-1>", lambda e, p=r: display_selected_photo(app, p, subjects))
            except Exception as e:
                ttk.Label(photo_frame, text=f"Error: {e}").grid(row=0, column=0, rowspan=2, padx=10, pady=10)
            details_frame = ttk.Frame(photo_frame, style="TFrame")
            details_frame.grid(row=0, column=1, sticky="w", padx=10)
            ttk.Label(details_frame, text=f"File: {r[1]}\nDate: {r[2]}\nLocation: {r[3]}\nLat: {r[4]}° {r[5]:.3f}'\nLon: {r[6]}° {r[7]:.3f}'\nRating: {r[8]}", justify="left").pack(anchor="w")
            ttk.Label(details_frame, text="Subjects:", style="Header.TLabel").pack(anchor="w", pady=5)
            subj_text = ""
            for subj in [s for s in subjects if s[1] == r[0]]:
                subj_text += f"Organism: {subj[2]}\nRating: {subj[3]}\nSex: {subj[4]}\nJuvenile: {subj[5]}\nFlying: {subj[6]}\nFlowers: {subj[7]}\nLeaves: {subj[8]}\nTrunk/Stem: {subj[9]}\nFruit: {subj[10]}\nNotes: {subj[11]}\n\n"
            subjects_label = ttk.Label(details_frame, text=subj_text or "No subjects", justify="left", wraplength=500)
            subjects_label.pack(anchor="w")
            ttk.Button(photo_frame, text="Edit", command=lambda pid=r[0]: app.edit_photo_page(pid), style="Primary.TButton").grid(row=0, column=2, padx=10, pady=10, sticky="ne")

    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
    ttk.Button(button_frame, text="Search", command=search, style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Back", command=app.create_home_page, style="Secondary.TButton").grid(row=0, column=1, padx=10)

def display_selected_photo(app, photo, subjects):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Selected Photo", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
    image_frame = ttk.Frame(main_frame, style="Card.TFrame")
    image_frame.grid(row=1, column=0, sticky="nsew", padx=10)
    image_label = ttk.Label(image_frame)
    image_label.pack(pady=10)
    details_frame = ttk.Frame(main_frame, style="Card.TFrame")
    details_frame.grid(row=1, column=1, sticky="nsew", padx=10)
    main_frame.grid_columnconfigure(0, weight=3)
    main_frame.grid_columnconfigure(1, weight=2)
    main_frame.grid_rowconfigure(1, weight=1)

    try:
        img = Image.open(photo[1])
        img.thumbnail((800, 600))
        photo_img = ImageTk.PhotoImage(img)
        image_label.configure(image=photo_img)
        image_label.image = photo_img
    except Exception as e:
        image_label.configure(image=None, text=f"Error loading image: {e}")

    ttk.Label(details_frame, text="Photo Details", style="Header.TLabel").pack(pady=5)
    photo_details = ttk.Label(details_frame, text=f"File: {photo[1]}\nDate: {photo[2]}\nLocation: {photo[3]}\nLat: {photo[4]}° {photo[5]:.3f}'\nLon: {photo[6]}° {photo[7]:.3f}'\nRating: {photo[8]}", justify="left")
    photo_details.pack(anchor="w", padx=10)
    ttk.Separator(details_frame, orient="horizontal").pack(fill="x", pady=10)
    ttk.Label(details_frame, text="Subjects", style="Header.TLabel").pack(pady=5)
    subjects_canvas = tk.Canvas(details_frame, bg="#FFFFFF")
    subjects_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=subjects_canvas.yview)
    subjects_frame = ttk.Frame(subjects_canvas, style="TFrame")
    subjects_frame.bind("<Configure>", lambda e: subjects_canvas.configure(scrollregion=subjects_canvas.bbox("all")))
    subjects_canvas.create_window((0, 0), window=subjects_frame, anchor="nw")
    subjects_canvas.configure(yscrollcommand=subjects_scroll.set)
    subjects_canvas.pack(side="left", fill="both", expand=True, padx=10)
    subjects_scroll.pack(side="right", fill="y")
    subj_text = ""
    for subj in [s for s in subjects if s[1] == photo[0]]:
        subj_text += f"Organism: {subj[2]}\nRating: {subj[3]}\nSex: {subj[4]}\nJuvenile: {subj[5]}\nFlying: {subj[6]}\nFlowers: {subj[7]}\nLeaves: {subj[8]}\nTrunk/Stem: {subj[9]}\nFruit: {subj[10]}\nNotes: {subj[11]}\n\n"
    subjects_text = ttk.Label(subjects_frame, text=subj_text or "No subjects", justify="left", wraplength=300)
    subjects_text.pack(anchor="w", padx=10, pady=5)

    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.grid(row=2, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="Edit Photo", command=lambda: app.edit_photo_page(photo[0]), style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Close", command=app.search_photos_page, style="Secondary.TButton").grid(row=0, column=1, padx=10)