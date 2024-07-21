from tkinter import messagebox


class PreferencesManager:
    def __init__(self, filename="preferences.txt"):
        self.filename = filename
        self.items_per_page = 20
        self.tolerance = 5

    def load_preferences(self):
        try:
            with open(self.filename, "r") as f:
                lines = f.readlines()
                self.tolerance = int(lines[0].strip()) if len(lines) > 0 else 5
                self.items_per_page = int(lines[1].strip()) if len(lines) > 1 else 20
        except (FileNotFoundError, IndexError, ValueError):
            self.tolerance = 5
            self.items_per_page = 20

    def save_preferences(self):
        try:
            with open(self.filename, "w") as f:
                f.write(f"{self.tolerance}\n")
                f.write(f"{self.items_per_page}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
