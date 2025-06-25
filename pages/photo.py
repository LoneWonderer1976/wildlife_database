import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import exifread
from decimal import Decimal

def add_photo_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="Card.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Add Photo", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
    file_path = tk.StringVar()
    fields = [
        ("Select Photo:", ttk.Button(main_frame, text="Browse", command=lambda: file_path.set(filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])))),
        ("File Path:", ttk.Label(main_frame, textvariable=file_path)),
        ("Date Taken:", ttk.Entry(main_frame)),
        ("Location:", ttk.Entry(main_frame)),
        ("Latitude Degrees:", ttk.Entry(main_frame)),
        ("Latitude Minutes:", ttk.Entry(main_frame)),
        ("Longitude Degrees:", ttk.Entry(main_frame)),
        ("Longitude Minutes:", ttk.Entry(main_frame)),
        ("Rating:", ttk.Entry(main_frame)),
        ("Number of Subjects:", ttk.Entry(main_frame))
    ]
    for i, (label, widget) in enumerate(fields, 1):
        ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=5)
        widget.grid(row=i, column=1, sticky="w", padx=10, pady=5)

    def load_metadata():
        if file_path.get():
            with open(file_path.get(), 'rb') as f:
                tags = exifread.process_file(f)
                if 'EXIF DateTimeOriginal' in tags:
                    fields[2][1].delete(0, tk.END)
                    fields[2][1].insert(0, str(tags['EXIF DateTimeOriginal']))
                if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                    lat = tags['GPS GPSLatitude'].values
                    lon = tags['GPS GPSLongitude'].values
                    lat_deg = lat[0].num
                    lat_min = round(Decimal(lat[1].num) / Decimal(lat[1].den) + Decimal(lat[2].num) / Decimal(lat[2].den) / 60, 3)
                    lon_deg = lon[0].num
                    lon_min = round(Decimal(lon[1].num) / Decimal(lon[1].den) + Decimal(lon[2].num) / Decimal(lon[2].den) / 60, 3)
                    fields[4][1].delete(0, tk.END)
                    fields[4][1].insert(0, lat_deg)
                    fields[5][1].delete(0, tk.END)
                    fields[5][1].insert(0, lat_min)
                    fields[6][1].delete(0, tk.END)
                    fields[6][1].insert(0, lon_deg)
                    fields[7][1].delete(0, tk.END)
                    fields[7][1].insert(0, lon_min)

    ttk.Button(main_frame, text="Load Metadata", command=load_metadata, style="Primary.TButton").grid(row=len(fields)+1, column=1, sticky="w", padx=10, pady=5)

    subjects_frame = ttk.Frame(main_frame, style="TFrame")
    subjects_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=10, sticky="ew")
    subject_entries = []

    def add_subject_fields():
        subject_frame = ttk.Frame(subjects_frame, style="Card.TFrame")
        subject_frame.pack(fill="x", padx=5, pady=5)
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        c.execute("SELECT organism_id, name FROM organisms")
        organisms = c.fetchall()
        conn.close()
        organism_var = tk.StringVar()
        ttk.Combobox(subject_frame, textvariable=organism_var, values=[o[1] for o in organisms], state="readonly").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(subject_frame, text="Rating:").grid(row=0, column=1, padx=5, pady=5)
        subj_rating = ttk.Entry(subject_frame, width=5)
        subj_rating.grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(subject_frame, text="Sex:").grid(row=0, column=3, padx=5, pady=5)
        sex = ttk.Entry(subject_frame, width=10)
        sex.grid(row=0, column=4, padx=5, pady=5)
        juvenile_var = tk.BooleanVar()
        ttk.Checkbutton(subject_frame, text="Juvenile", variable=juvenile_var).grid(row=0, column=5, padx=5, pady=5)
        flying_var = tk.BooleanVar()
        ttk.Checkbutton(subject_frame, text="Flying", variable=flying_var).grid(row=0, column=6, padx=5, pady=5)
        flowers_var = tk.BooleanVar()
        ttk.Checkbutton(subject_frame, text="Flowers", variable=flowers_var).grid(row=1, column=0, padx=5, pady=5)
        leaves_var = tk.BooleanVar()
        ttk.Checkbutton(subject_frame, text="Leaves", variable=leaves_var).grid(row=1, column=1, padx=5, pady=5)
        trunk_var = tk.BooleanVar()
        ttk.Checkbutton(subject_frame, text="Trunk/Stem", variable=trunk_var).grid(row=1, column=2, padx=5, pady=5)
        fruit_var = tk.BooleanVar()
        ttk.Checkbutton(subject_frame, text="Fruit", variable=fruit_var).grid(row=1, column=3, padx=5, pady=5)
        ttk.Label(subject_frame, text="Notes:").grid(row=1, column=4, padx=5, pady=5)
        notes = ttk.Entry(subject_frame)
        notes.grid(row=1, column=5, columnspan=2, padx=5, pady=5, sticky="ew")
        subject_entries.append((organism_var, subj_rating, sex, juvenile_var, flying_var, flowers_var, leaves_var, trunk_var, fruit_var, notes, organisms))

    def add_multiple_subjects():
        try:
            count = int(fields[9][1].get() or 0)
            for _ in range(count):
                add_subject_fields()
        except ValueError:
            messagebox.showerror("Error", "Number of subjects must be a number")

    ttk.Button(main_frame, text="Add Subject Fields", command=add_multiple_subjects, style="Primary.TButton").grid(row=len(fields)+3, column=1, sticky="w", padx=10, pady=5)

    def save_photo():
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        try:
            lat_min = round(float(fields[5][1].get() or 0), 3)
            lon_min = round(float(fields[7][1].get() or 0), 3)
            c.execute("INSERT INTO photos (file_path, date_taken, location, lat_degrees, lat_minutes, lon_degrees, lon_minutes, rating, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (file_path.get(), fields[2][1].get(), fields[3][1].get(), int(fields[4][1].get() or 0),
                       lat_min, int(fields[6][1].get() or 0), lon_min,
                       int(fields[8][1].get() or 0), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            photo_id = c.lastrowid
            for subj in subject_entries:
                org_id = [o[0] for o in subj[10] if o[1] == subj[0].get()][0] if subj[0].get() else None
                c.execute("INSERT INTO photo_subjects (photo_id, organism_id, subject_rating, subject_sex, is_juvenile, is_flying, has_flowers, has_leaves, has_trunk_stem, has_fruit, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (photo_id, org_id, int(subj[1].get() or 0), subj[2].get(), "Yes" if subj[3].get() else "No",
                           "Yes" if subj[4].get() else "No", "Yes" if subj[5].get() else "No", "Yes" if subj[6].get() else "No",
                           "Yes" if subj[7].get() else "No", "Yes" if subj[8].get() else "No", subj[9].get()))
            conn.commit()
            messagebox.showinfo("Success", "Photo and subjects added")
            app.create_home_page()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Failed to save photo: {e}. Please ensure the database schema is updated.")
        finally:
            conn.close()

    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.grid(row=len(fields)+4, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="Save", command=save_photo, style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Back", command=app.create_home_page, style="Secondary.TButton").grid(row=0, column=1, padx=10)

def browse_options_page(app):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="Card.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="Browse Photos Options", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
    browse_mode = tk.StringVar(value="Chronological")
    ttk.Label(main_frame, text="Browse Mode:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    ttk.Combobox(main_frame, textvariable=browse_mode, values=[
        "Chronological", "Date Added", "Organism Type", "Page Number", "Rating", "Random"
    ], state="readonly").grid(row=1, column=1, sticky="w", padx=10, pady=5)

    input_frame = ttk.Frame(main_frame, style="TFrame")
    input_frame.grid(row=2, column=0, columnspan=2, pady=10)
    conn = sqlite3.connect("wildlife.db")
    c = conn.cursor()
    c.execute("SELECT type_id, type_name FROM organism_types")
    types = c.fetchall()
    c.execute("SELECT DISTINCT book_page FROM organisms WHERE book_page IS NOT NULL")
    pages = [str(p[0]) for p in c.fetchall()]
    c.execute("SELECT DISTINCT rating FROM photos WHERE rating IS NOT NULL")
    ratings = [str(r[0]) for r in c.fetchall()]
    conn.close()

    type_var = tk.StringVar()
    page_var = tk.StringVar()
    rating_var = tk.StringVar()
    type_label = ttk.Label(input_frame, text="Organism Type:")
    type_combobox = ttk.Combobox(input_frame, textvariable=type_var, values=[t[1] for t in types], state="readonly")
    page_label = ttk.Label(input_frame, text="Page Number:")
    page_entry = ttk.Entry(input_frame, textvariable=page_var)
    rating_label = ttk.Label(input_frame, text="Rating:")
    rating_combobox = ttk.Combobox(input_frame, textvariable=rating_var, values=ratings, state="readonly")

    def update_inputs(*args):
        for widget in input_frame.winfo_children():
            widget.grid_forget()
        mode = browse_mode.get()
        if mode == "Organism Type":
            type_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)
            type_combobox.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        elif mode == "Page Number":
            page_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)
            page_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        elif mode == "Rating":
            rating_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)
            rating_combobox.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    browse_mode.trace("w", update_inputs)
    update_inputs()

    def proceed():
        mode = browse_mode.get()
        filter_value = None
        if mode == "Organism Type":
            filter_value = [t[0] for t in types if t[1] == type_var.get()][0] if type_var.get() else None
        elif mode == "Page Number":
            filter_value = page_var.get()
        elif mode == "Rating":
            filter_value = rating_var.get()
        browse_photos_page(app, mode, filter_value)

    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.grid(row=3, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="Proceed", command=proceed, style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Back", command=app.create_home_page, style="Secondary.TButton").grid(row=0, column=1, padx=10)

def browse_photos_page(app, browse_mode="Chronological", filter_value=None):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    ttk.Label(main_frame, text=f"Browse Photos ({browse_mode})", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
    conn = sqlite3.connect("wildlife.db")
    c = conn.cursor()
    query = "SELECT photo_id, file_path, date_taken, location, lat_degrees, lat_minutes, lon_degrees, lon_minutes, rating FROM photos"
    params = []
    joins = ""
    if browse_mode == "Organism Type" and filter_value:
        joins = " LEFT JOIN photo_subjects ps ON photos.photo_id = ps.photo_id LEFT JOIN organisms o ON ps.organism_id = o.organism_id"
        query += joins + " WHERE o.type_id = ?"
        params.append(filter_value)
    elif browse_mode == "Page Number" and filter_value:
        joins = " LEFT JOIN photo_subjects ps ON photos.photo_id = ps.photo_id LEFT JOIN organisms o ON ps.organism_id = o.organism_id"
        query += joins + " WHERE o.book_page = ?"
        params.append(int(filter_value))
    elif browse_mode == "Rating" and filter_value:
        query += " WHERE rating = ?"
        params.append(int(filter_value))
    
    if browse_mode == "Chronological":
        query += " ORDER BY date_taken"
    elif browse_mode == "Date Added":
        query += " ORDER BY date_added"
    elif browse_mode == "Random":
        query += " ORDER BY RANDOM()"
    elif browse_mode in ["Organism Type", "Page Number", "Rating"]:
        query += " ORDER BY photo_id"
    else:
        query += " ORDER BY photo_id"

    c.execute(query, params)
    photos = c.fetchall()
    c.execute("SELECT ps.subject_id, ps.photo_id, o.name, ps.subject_rating, ps.subject_sex, ps.is_juvenile, ps.is_flying, ps.has_flowers, ps.has_leaves, ps.has_trunk_stem, ps.has_fruit, ps.notes FROM photo_subjects ps LEFT JOIN organisms o ON ps.organism_id = o.organism_id")
    subjects = c.fetchall()
    conn.close()

    current_photo = tk.IntVar(value=0)
    image_frame = ttk.Frame(main_frame, style="Card.TFrame")
    image_frame.grid(row=1, column=0, sticky="nsew", padx=10)
    image_label = ttk.Label(image_frame)
    image_label.pack(pady=10)
    details_frame = ttk.Frame(main_frame, style="Card.TFrame")
    details_frame.grid(row=1, column=1, sticky="nsew", padx=10)
    main_frame.grid_columnconfigure(0, weight=3)
    main_frame.grid_columnconfigure(1, weight=2)
    main_frame.grid_rowconfigure(1, weight=1)

    ttk.Label(details_frame, text="Photo Details", style="Header.TLabel").pack(pady=5)
    photo_details = ttk.Label(details_frame, text="", justify="left")
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
    subjects_text = ttk.Label(subjects_frame, text="", justify="left", wraplength=300)
    subjects_text.pack(anchor="w", padx=10, pady=5)

    def update_display():
        subjects_text.configure(text="")
        if photos:
            photo = photos[current_photo.get()]
            try:
                img = Image.open(photo[1])
                img.thumbnail((800, 600))
                photo_img = ImageTk.PhotoImage(img)
                image_label.configure(image=photo_img)
                image_label.image = photo_img
            except Exception as e:
                image_label.configure(image=None, text=f"Error loading image: {e}")
            photo_details.configure(text=f"File: {photo[1]}\nDate: {photo[2]}\nLocation: {photo[3]}\nLat: {photo[4]}° {photo[5]:.3f}'\nLon: {photo[6]}° {photo[7]:.3f}'\nRating: {photo[8]}")
            subj_text = ""
            for subj in [s for s in subjects if s[1] == photo[0]]:
                subj_text += f"Organism: {subj[2]}\nRating: {subj[3]}\nSex: {subj[4]}\nJuvenile: {subj[5]}\nFlying: {subj[6]}\nFlowers: {subj[7]}\nLeaves: {subj[8]}\nTrunk/Stem: {subj[9]}\nFruit: {subj[10]}\nNotes: {subj[11]}\n\n"
            subjects_text.configure(text=subj_text or "No subjects")
        else:
            image_label.configure(image=None, text="No photos available")
            photo_details.configure(text="")
            subjects_text.configure(text="No subjects")

    update_display()
    nav_frame = ttk.Frame(main_frame, style="TFrame")
    nav_frame.grid(row=2, column=0, columnspan=2, pady=20)
    ttk.Button(nav_frame, text="Previous", command=lambda: [current_photo.set(max(0, current_photo.get()-1)), update_display()], style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(nav_frame, text="Next", command=lambda: [current_photo.set(min(len(photos)-1, current_photo.get()+1)), update_display()], style="Primary.TButton").grid(row=0, column=1, padx=10)
    ttk.Button(nav_frame, text="Edit Photo", command=lambda: edit_photo_page(app, photos[current_photo.get()][0]) if photos else None, style="Primary.TButton").grid(row=0, column=2, padx=10)
    ttk.Button(nav_frame, text="Back", command=app.browse_options_page, style="Secondary.TButton").grid(row=0, column=3, padx=10)

def edit_photo_page(app, photo_id):
    for widget in app.winfo_children():
        widget.destroy()
    main_frame = ttk.Frame(app, style="Card.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    conn = sqlite3.connect("wildlife.db")
    c = conn.cursor()
    c.execute("SELECT file_path, date_taken, location, lat_degrees, lat_minutes, lon_degrees, lon_minutes, rating FROM photos WHERE photo_id = ?", (photo_id,))
    photo = c.fetchone()
    c.execute("SELECT subject_id, organism_id, subject_rating, subject_sex, is_juvenile, is_flying, has_flowers, has_leaves, has_trunk_stem, has_fruit, notes FROM photo_subjects WHERE photo_id = ?", (photo_id,))
    subjects = c.fetchall()
    c.execute("SELECT organism_id, name FROM organisms")
    organisms = c.fetchall()
    conn.close()

    ttk.Label(main_frame, text="Edit Photo", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)
    try:
        img = Image.open(photo[0])
        img.thumbnail((150, 150))
        photo_img = ImageTk.PhotoImage(img)
        ttk.Label(main_frame, image=photo_img).grid(row=1, column=0, columnspan=2, pady=5)
        main_frame.image = photo_img
    except Exception as e:
        ttk.Label(main_frame, text=f"Thumbnail error: {e}").grid(row=1, column=0, columnspan=2, pady=5)

    fields = [
        ("File Path:", ttk.Label(main_frame, text=photo[0])),
        ("Date Taken:", ttk.Entry(main_frame)),
        ("Location:", ttk.Entry(main_frame)),
        ("Latitude Degrees:", ttk.Entry(main_frame)),
        ("Latitude Minutes:", ttk.Entry(main_frame)),
        ("Longitude Degrees:", ttk.Entry(main_frame)),
        ("Longitude Minutes:", ttk.Entry(main_frame)),
        ("Rating:", ttk.Entry(main_frame))
    ]
    for i, (label, widget) in enumerate(fields, 2):
        ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=5)
        widget.grid(row=i, column=1, sticky="w", padx=10, pady=5)
    for i, value in enumerate(photo[1:], 1):
        if value is not None:
            if i in [4, 6]:  # lat_minutes, lon_minutes
                value = f"{value:.3f}"
            fields[i][1].insert(0, value)

    subjects_frame = ttk.Frame(main_frame, style="TFrame")
    subjects_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=10, sticky="ew")
    subject_entries = []

    def add_subject_fields(subject=None, subject_id=None):
        subject_frame = ttk.Frame(subjects_frame, style="Card.TFrame")
        subject_frame.pack(fill="x", padx=5, pady=5)
        organism_var = tk.StringVar()
        if subject and subject[1]:
            matching_orgs = [o[1] for o in organisms if o[0] == subject[1]]
            current_org = matching_orgs[0] if matching_orgs else ""
        else:
            current_org = ""
        ttk.Combobox(subject_frame, textvariable=organism_var, values=[o[1] for o in organisms], state="readonly").grid(row=0, column=0, padx=5, pady=5)
        organism_var.set(current_org)
        ttk.Label(subject_frame, text="Rating:").grid(row=0, column=1, padx=5, pady=5)
        subj_rating = ttk.Entry(subject_frame, width=5)
        subj_rating.grid(row=0, column=2, padx=5, pady=5)
        subj_rating.insert(0, subject[2] or 0 if subject else 0)
        ttk.Label(subject_frame, text="Sex:").grid(row=0, column=3, padx=5, pady=5)
        sex = ttk.Entry(subject_frame, width=10)
        sex.grid(row=0, column=4, padx=5, pady=5)
        sex.insert(0, subject[3] or "" if subject else "")
        juvenile_var = tk.BooleanVar(value=subject[4] == "Yes" if subject else False)
        ttk.Checkbutton(subject_frame, text="Juvenile", variable=juvenile_var).grid(row=0, column=5, padx=5, pady=5)
        flying_var = tk.BooleanVar(value=subject[5] == "Yes" if subject else False)
        ttk.Checkbutton(subject_frame, text="Flying", variable=flying_var).grid(row=0, column=6, padx=5, pady=5)
        flowers_var = tk.BooleanVar(value=subject[6] == "Yes" if subject else False)
        ttk.Checkbutton(subject_frame, text="Flowers", variable=flowers_var).grid(row=1, column=0, padx=5, pady=5)
        leaves_var = tk.BooleanVar(value=subject[7] == "Yes" if subject else False)
        ttk.Checkbutton(subject_frame, text="Leaves", variable=leaves_var).grid(row=1, column=1, padx=5, pady=5)
        trunk_var = tk.BooleanVar(value=subject[8] == "Yes" if subject else False)
        ttk.Checkbutton(subject_frame, text="Trunk/Stem", variable=trunk_var).grid(row=1, column=2, padx=5, pady=5)
        fruit_var = tk.BooleanVar(value=subject[9] == "Yes" if subject else False)
        ttk.Checkbutton(subject_frame, text="Fruit", variable=fruit_var).grid(row=1, column=3, padx=5, pady=5)
        ttk.Label(subject_frame, text="Notes:").grid(row=1, column=4, padx=5, pady=5)
        notes = ttk.Entry(subject_frame)
        notes.grid(row=1, column=5, columnspan=2, padx=5, pady=5, sticky="ew")
        notes.insert(0, subject[10] or "" if subject else "")
        if subject:
            ttk.Button(subject_frame, text="Remove", command=lambda: [subject_frame.destroy(), subject_entries.remove((subject_id, organism_var, subj_rating, sex, juvenile_var, flying_var, flowers_var, leaves_var, trunk_var, fruit_var, notes))], style="Secondary.TButton").grid(row=0, column=7, padx=5, pady=5)
        subject_entries.append((subject_id, organism_var, subj_rating, sex, juvenile_var, flying_var, flowers_var, leaves_var, trunk_var, fruit_var, notes))

    for subj in subjects:
        add_subject_fields(subj, subj[0])

    ttk.Button(main_frame, text="Add New Subject", command=lambda: add_subject_fields(), style="Primary.TButton").grid(row=len(fields)+3, column=1, sticky="w", padx=10, pady=5)

    def save_changes():
        conn = sqlite3.connect("wildlife.db")
        c = conn.cursor()
        try:
            lat_min = round(float(fields[4][1].get() or 0), 3)
            lon_min = round(float(fields[6][1].get() or 0), 3)
            c.execute("UPDATE photos SET date_taken = ?, location = ?, lat_degrees = ?, lat_minutes = ?, lon_degrees = ?, lon_minutes = ?, rating = ? WHERE photo_id = ?",
                      (fields[1][1].get(), fields[2][1].get(), int(fields[3][1].get() or 0), lat_min,
                       int(fields[5][1].get() or 0), lon_min, int(fields[7][1].get() or 0), photo_id))
            c.execute("DELETE FROM photo_subjects WHERE photo_id = ?", (photo_id,))
            for subj in subject_entries:
                org_id = [o[0] for o in organisms if o[1] == subj[1].get()][0] if subj[1].get() else None
                c.execute("INSERT INTO photo_subjects (photo_id, organism_id, subject_rating, subject_sex, is_juvenile, is_flying, has_flowers, has_leaves, has_trunk_stem, has_fruit, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (photo_id, org_id, int(subj[2].get() or 0), subj[3].get(), "Yes" if subj[4].get() else "No",
                           "Yes" if subj[5].get() else "No", "Yes" if subj[6].get() else "No", "Yes" if subj[7].get() else "No",
                           "Yes" if subj[8].get() else "No", "Yes" if subj[9].get() else "No", subj[10].get()))
            conn.commit()
            messagebox.showinfo("Success", "Changes saved")
            app.browse_options_page()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Failed to save changes: {e}. Please ensure the database schema is updated.")
        finally:
            conn.close()

    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.grid(row=len(fields)+4, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="Save Changes", command=save_changes, style="Primary.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Cancel", command=app.browse_options_page, style="Secondary.TButton").grid(row=0, column=1, padx=10)