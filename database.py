import sqlite3
from decimal import Decimal

def init_db():
    conn = sqlite3.connect("wildlife.db")
    c = conn.cursor()
    # Create organism_types table
    c.execute('''CREATE TABLE IF NOT EXISTS organism_types (
                 type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 type_name TEXT NOT NULL UNIQUE)''')
    # Create subtypes table
    c.execute('''CREATE TABLE IF NOT EXISTS subtypes (
                 subtype_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 type_id INTEGER,
                 subtype_name TEXT NOT NULL,
                 UNIQUE(type_id, subtype_name),
                 FOREIGN KEY (type_id) REFERENCES organism_types(type_id))''')
    # Create organisms table
    c.execute('''CREATE TABLE IF NOT EXISTS organisms (
                 organism_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 type_id INTEGER,
                 subtype_id INTEGER,
                 name TEXT,
                 genus TEXT,
                 species TEXT,
                 book_page INTEGER,
                 page_position INTEGER,
                 FOREIGN KEY (type_id) REFERENCES organism_types(type_id),
                 FOREIGN KEY (subtype_id) REFERENCES subtypes(subtype_id))''')
    # Create book_pages table
    c.execute('''CREATE TABLE IF NOT EXISTS book_pages (
                 page_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 page_number INTEGER UNIQUE,
                 num_organisms INTEGER)''')
    # Create page_types table
    c.execute('''CREATE TABLE IF NOT EXISTS page_types (
                 page_id INTEGER,
                 type_id INTEGER,
                 PRIMARY KEY (page_id, type_id),
                 FOREIGN KEY (page_id) REFERENCES book_pages(page_id),
                 FOREIGN KEY (type_id) REFERENCES organism_types(type_id))''')
    # Create page_subtypes table
    c.execute('''CREATE TABLE IF NOT EXISTS page_subtypes (
                 page_id INTEGER,
                 subtype_id INTEGER,
                 PRIMARY KEY (page_id, subtype_id),
                 FOREIGN KEY (page_id) REFERENCES book_pages(page_id),
                 FOREIGN KEY (subtype_id) REFERENCES subtypes(subtype_id))''')
    # Create photos table
    c.execute('''CREATE TABLE IF NOT EXISTS photos (
                 photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 file_path TEXT NOT NULL,
                 date_taken TEXT,
                 location TEXT,
                 lat_degrees INTEGER,
                 lat_minutes DECIMAL(10,3),
                 lon_degrees INTEGER,
                 lon_minutes DECIMAL(10,3),
                 rating INTEGER,
                 date_added TEXT)''')
    # Schema migration for photos table
    c.execute("PRAGMA table_info(photos)")
    columns = {col[1]: col[2] for col in c.fetchall()}
    if 'date_added' not in columns:
        c.execute("ALTER TABLE photos ADD COLUMN date_added TEXT")
        c.execute("UPDATE photos SET date_added = '2025-01-01 00:00:00' WHERE date_added IS NULL")
    if columns.get('lat_minutes') != 'DECIMAL(10,3)' or columns.get('lon_minutes') != 'DECIMAL(10,3)':
        c.execute("ALTER TABLE photos RENAME TO photos_old")
        c.execute('''CREATE TABLE photos (
                     photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     file_path TEXT NOT NULL,
                     date_taken TEXT,
                     location TEXT,
                     lat_degrees INTEGER,
                     lat_minutes DECIMAL(10,3),
                     lon_degrees INTEGER,
                     lon_minutes DECIMAL(10,3),
                     rating INTEGER,
                     date_added TEXT)''')
        c.execute('''INSERT INTO photos (photo_id, file_path, date_taken, location, lat_degrees, lat_minutes, lon_degrees, lon_minutes, rating, date_added)
                     SELECT photo_id, file_path, date_taken, location, lat_degrees, ROUND(lat_minutes, 3), lon_degrees, ROUND(lon_minutes, 3), rating, date_added
                     FROM photos_old''')
        c.execute("DROP TABLE photos_old")
    # Create photo_subjects table
    c.execute('''CREATE TABLE IF NOT EXISTS photo_subjects (
                 subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 photo_id INTEGER,
                 organism_id INTEGER,
                 subject_rating INTEGER,
                 subject_sex TEXT,
                 is_juvenile TEXT,
                 is_flying TEXT,
                 has_flowers TEXT,
                 has_leaves TEXT,
                 has_trunk_stem TEXT,
                 has_fruit TEXT,
                 notes TEXT,
                 FOREIGN KEY (photo_id) REFERENCES photos(photo_id),
                 FOREIGN KEY (organism_id) REFERENCES organisms(organism_id))''')
    # Schema migration for organisms table
    c.execute("PRAGMA table_info(organisms)")
    columns = {col[1]: col[2] for col in c.fetchall()}
    if 'subtype_id' not in columns:
        c.execute("ALTER TABLE organisms ADD COLUMN subtype_id INTEGER")
        c.execute("UPDATE organisms SET subtype_id = NULL")
    # Schema migration for book_pages table
    c.execute("PRAGMA table_info(book_pages)")
    columns = {col[1]: col[2] for col in c.fetchall()}
    if 'type_id' in columns:
        c.execute("SELECT page_id, type_id FROM book_pages WHERE type_id IS NOT NULL")
        for page_id, type_id in c.fetchall():
            c.execute("INSERT OR IGNORE INTO page_types (page_id, type_id) VALUES (?, ?)", (page_id, type_id))
        c.execute("CREATE TABLE book_pages_new (page_id INTEGER PRIMARY KEY AUTOINCREMENT, page_number INTEGER UNIQUE, num_organisms INTEGER)")
        c.execute("INSERT INTO book_pages_new (page_id, page_number, num_organisms) SELECT page_id, page_number, num_organisms FROM book_pages")
        c.execute("DROP TABLE book_pages")
        c.execute("ALTER TABLE book_pages_new RENAME TO book_pages")
    conn.commit()
    conn.close()