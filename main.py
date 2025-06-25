import tkinter as tk
from database import init_db
from ui_components import setup_styles
from pages.home import create_home_page
from pages.organism_type import add_organism_type_page
from pages.organism import add_organism_page
from pages.book_page import add_page_page
from pages.photo import add_photo_page, browse_options_page, browse_photos_page, edit_photo_page
from pages.search import search_photos_page, display_selected_photo

class WildlifeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wildlife Database")
        self.geometry("1200x800")
        self.configure(bg="#E6F0FA")
        init_db()
        setup_styles(self)
        self.search_state = None

        # Bind page methods directly as instance attributes
        self.create_home_page = self._bind(create_home_page)
        self.add_organism_type_page = self._bind(add_organism_type_page)
        self.add_organism_page = self._bind(add_organism_page)
        self.add_page_page = self._bind(add_page_page)
        self.add_photo_page = self._bind(add_photo_page)
        self.browse_options_page = self._bind(browse_options_page)
        self.browse_photos_page = self._bind(browse_photos_page)
        self.edit_photo_page = self._bind(edit_photo_page)
        self.search_photos_page = self._bind(search_photos_page)
        self.display_selected_photo = self._bind(display_selected_photo)

        # Initialize the home page
        self.create_home_page()

    def _bind(self, func):
        """Helper to bind a function to the instance, passing self as the first argument."""
        def wrapped(*args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapped

if __name__ == "__main__":
    try:
        app = WildlifeApp()
        app.mainloop()
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(str(e))
        print(f"Error: {e}")
        input("Press Enter to exit...")