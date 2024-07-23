import yaml
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox


class PreferencesManager:
    def __init__(self, filename="preferences.yaml"):
        self.filename = filename
        self.items_per_page = 20
        self.tolerance = 5

    def load_preferences(self):
        if not os.path.exists(self.filename):
            self.save_default_preferences()
            return

        try:
            with open(self.filename, "r") as f:
                preferences = yaml.safe_load(f) or {}
                self.items_per_page = preferences.get('pagination', {}).get('items_per_page', 20)
                self.tolerance = preferences.get('system', {}).get('image_tolerance', 5)
        except yaml.YAMLError as e:
            messagebox.showerror("Error", f"Failed to load preferences: {e}")
            self.save_default_preferences()

    def save_preferences(self):
        try:
            preferences = {
                'pagination': {'items_per_page': self.items_per_page},
                'system': {'image_tolerance': self.tolerance}
            }
            with open(self.filename, "w") as f:
                yaml.safe_dump(preferences, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {e}")

    def save_default_preferences(self):
        self.items_per_page = 20
        self.tolerance = 5
        self.save_preferences()

    def open_preferences(self, root, update_pagination, load_page, current_page):
        pref_window = tk.Toplevel(root)
        pref_window.title("Preferences")
        pref_frame = ctk.CTkFrame(pref_window)
        pref_frame.pack(padx=10, pady=10)

        tolerance_label = ctk.CTkLabel(pref_frame, text="Tolerance Level:")
        tolerance_label.grid(row=0, column=0, pady=5, sticky='w')
        tolerance_entry = ctk.CTkEntry(pref_frame)
        tolerance_entry.grid(row=0, column=1, pady=5, sticky='w')
        tolerance_entry.insert(0, str(self.tolerance))

        items_label = ctk.CTkLabel(pref_frame, text="Items Per Page:")
        items_label.grid(row=1, column=0, pady=5, sticky='w')
        items_entry = ctk.CTkEntry(pref_frame)
        items_entry.grid(row=1, column=1, pady=5, sticky='w')
        items_entry.insert(0, str(self.items_per_page))

        def save_preferences_and_close():
            try:
                self.tolerance = int(tolerance_entry.get())
                self.items_per_page = int(items_entry.get())
                self.save_preferences()
                pref_window.destroy()
                update_pagination()
                root.after(0, load_page, current_page)  # Schedule on main thread
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid integers for tolerance and items per page.")

        save_button = ctk.CTkButton(pref_frame, text="Save", command=save_preferences_and_close)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)
