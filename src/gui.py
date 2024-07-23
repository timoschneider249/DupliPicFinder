import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
from image_utils import ImageUtils
from preferences import PreferencesManager


def show_about():
    messagebox.showinfo("About", "Dupli Pic Finder v0.5.0")


class DupliPicFinderApp:
    def __init__(self, root):
        self.next_button = None
        self.page_label = None
        self.prev_button = None
        self.pagination_frame = None
        self.result_frame = None
        self.canvas = None
        self.progress_label = None
        self.progress_bar = None
        self.select_all_button = None
        self.delete_all_button = None
        self.select_button = None
        self.controls_frame = None
        self.root = root
        self.current_page = 0
        self.total_items = 0
        self.unique_duplicates = []
        self.selected_for_deletion = []
        self.select_all_state = False
        self.preferences_manager = PreferencesManager()

        # Initialize the GUI components
        self.initialize_gui()
        self.preferences_manager.load_preferences()

    def initialize_gui(self):
        # Set window title and size
        self.root.title("DupliPicFinder")
        self.root.geometry("1200x800")

        # Create and configure the menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Select Folder", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        preferences_menu = tk.Menu(menu_bar, tearoff=0)
        preferences_menu.add_command(label="Preferences", command=self.open_preferences)
        menu_bar.add_cascade(label="Preferences", menu=preferences_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="About", command=show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Initialize control buttons and progress bar
        self.controls_frame = ctk.CTkFrame(self.root)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        self.controls_frame.grid_columnconfigure(0, weight=1)

        self.select_button = ctk.CTkButton(self.controls_frame, text="Select Folder", command=self.select_folder)
        self.select_button.grid(row=0, column=0, pady=10, padx=5, sticky='ew')

        self.delete_all_button = ctk.CTkButton(self.controls_frame, text="Delete Selected", command=self.delete_selected_images)
        self.delete_all_button.grid(row=0, column=1, pady=10, padx=5, sticky='ew')

        self.select_all_button = ctk.CTkButton(self.controls_frame, text="Select All", command=self.select_all_images)
        self.select_all_button.grid(row=0, column=2, pady=10, padx=5, sticky='ew')

        self.progress_bar = ctk.CTkProgressBar(self.root, width=500)
        self.progress_bar.grid(row=1, column=0, pady=5, padx=10, sticky='ew')

        self.progress_label = ctk.CTkLabel(self.root, text="0/0 images")
        self.progress_label.grid(row=2, column=0, pady=5, padx=10, sticky='ew')

        # Initialize canvas for displaying results
        self.canvas = tk.Canvas(self.root)
        self.canvas.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

        v_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        v_scrollbar.grid(row=3, column=1, padx=0, pady=10, sticky='ns')

        h_scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        h_scrollbar.grid(row=4, column=0, padx=10, pady=5, sticky='ew')

        self.result_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="center")

        self.result_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Initialize pagination controls
        self.pagination_frame = ctk.CTkFrame(self.root)
        self.pagination_frame.grid(row=5, column=0, pady=10, padx=10, sticky='ew')
        self.pagination_frame.grid_columnconfigure(0, weight=1)

        pagination_inner_frame = tk.Frame(self.pagination_frame)
        pagination_inner_frame.pack(expand=True, anchor='center')

        self.prev_button = ctk.CTkButton(pagination_inner_frame, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.page_label = ctk.CTkLabel(pagination_inner_frame, text="Page 1")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.next_button = ctk.CTkButton(pagination_inner_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Initialize status bar
        status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, padx=10, pady=5, sticky='ew')

        # Configure grid rows and columns
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Bind mouse wheel event for scrolling
        self.root.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_find_duplicates_complete(self, duplicates):
        self.unique_duplicates = list(set(tuple(sorted(dup)) for dup in duplicates))
        self.total_items = len(self.unique_duplicates)
        self.update_pagination()
        self.load_page(self.current_page)
        self.select_button.configure(state=tk.NORMAL)
        self.progress_label.configure(text=f"{self.total_items}/{self.total_items} images")
        self.progress_bar.set(1)

    def load_page(self, page_number):
        start_index = page_number * self.preferences_manager.items_per_page
        end_index = min(start_index + self.preferences_manager.items_per_page, self.total_items)

        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Create column headers
        headers = ['Index', 'Select', 'Duplicate 1', 'Duplicate 2']
        column_widths = [10, 15, 40, 40]

        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(self.result_frame, text=header, width=column_widths[col])
            header_label.grid(row=0, column=col, sticky='nsew')

            if col < len(headers) - 1:
                pipe_label = ctk.CTkLabel(self.result_frame, text='', width=2, bg_color='gray')
                pipe_label.grid(row=0, column=col + 1, sticky='ns', padx=(column_widths[col] // 2, 0))

        # Display duplicates
        for idx, dup in enumerate(self.unique_duplicates[start_index:end_index]):
            index = start_index + idx
            ctk.CTkLabel(self.result_frame, text=index + 1).grid(row=idx + 1, column=0, sticky='nsew')

            select_var = tk.BooleanVar(value=dup in self.selected_for_deletion)
            select_checkbox = ctk.CTkCheckBox(self.result_frame, text="Mark Delete", variable=select_var)
            select_checkbox.grid(row=idx + 1, column=1, sticky='ew')

            select_checkbox.bind("<Button-1>", lambda e, dups=dup: self.toggle_selection(dups))

            ctk.CTkLabel(self.result_frame, text=dup[0]).grid(row=idx + 1, column=2, sticky='nsew')
            ctk.CTkLabel(self.result_frame, text=dup[1]).grid(row=idx + 1, column=3, sticky='nsew')

        # Update scroll region
        self.result_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def toggle_selection(self, dup):
        if dup in self.selected_for_deletion:
            self.selected_for_deletion.remove(dup)
        else:
            self.selected_for_deletion.append(dup)
        self.load_page(self.current_page)

    def update_pagination(self):
        self.page_label.configure(text=f"Page {self.current_page + 1} of {-(self.total_items // -self.preferences_manager.items_per_page)}")
        self.prev_button.configure(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.configure(
            state=tk.NORMAL if self.current_page < (self.total_items - 1) // self.preferences_manager.items_per_page else tk.DISABLED)

    def next_page(self):
        if self.current_page < (self.total_items - 1) // self.preferences_manager.items_per_page:
            self.current_page += 1
            self.root.after(0, self.load_page, self.current_page)
            self.update_pagination()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.root.after(0, self.load_page, self.current_page)
            self.update_pagination()

    def update_progress(self, current, total, progress):
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{current}/{total} images")
        self.root.update_idletasks()

    def view_image(self, image_path):
        top = tk.Toplevel(self.root)
        top.title("View Image")
        img = Image.open(image_path)
        img = ImageTk.PhotoImage(img)
        label = tk.Label(top, image=img)
        label.image = img
        label.pack()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        tolerance = self.preferences_manager.tolerance
        try:
            tolerance = int(tolerance)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for tolerance.")
            return

        self.select_button.configure(state=tk.DISABLED)
        self.progress_label.configure(text="Processing...")
        self.root.update_idletasks()

        self.canvas.delete("all")

        self.result_frame.destroy()
        self.result_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="nw")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        thread = threading.Thread(target=ImageUtils.find_duplicates,
                                  args=(folder_path, tolerance, self.update_progress, self.on_find_duplicates_complete))
        thread.start()
        self.select_button.configure(state=tk.ACTIVE)

    def delete_selected_images(self):
        if len(self.selected_for_deletion) < 1:
            messagebox.showinfo("Invalid Input", "Please select at least one image to delete.")
        else:
            response = messagebox.askyesno("Delete Images", f"Are you sure you want to delete the {len(self.selected_for_deletion)} selected images?")
            if response:
                for dup in self.selected_for_deletion:
                    for img_path in dup:
                        if os.path.exists(img_path):
                            os.remove(img_path)

                messagebox.showinfo("Deleted", "Deleted selected images")
                self.selected_for_deletion.clear()
                self.select_folder()
            else:
                return

    def select_all_images(self):
        if self.select_all_state:
            self.selected_for_deletion.clear()
            self.select_all_state = False
            self.select_all_button.configure(text="Select All")
        else:
            self.selected_for_deletion = list(self.unique_duplicates)
            self.select_all_state = True
            self.select_all_button.configure(text="Deselect All")
        self.load_page(self.current_page)

    def show_help(self):
        top = tk.Toplevel(self.root)
        top.title("Help")
        help_text_area = ctk.CTkTextbox(top, height=15, width=90)
        help_text_area.insert("1.0", "More info on how to use this application...\n\n"
                                     "1. Select Folder: Use this button to choose a folder containing images.\n"
                                     "2. Tolerance Level: Enter the tolerance level for finding duplicates.\n"
                                     "3. Delete: Deletes the selected image from your system.\n"
                                     "4. View: Opens a new window to view the selected image.\n\n"
                                     "For more information, visit https://github.com/timoschneider249/DupliPicFinder")
        help_text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ctk.CTkScrollbar(top, command=help_text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text_area.configure(yscrollcommand=scrollbar.set)

    def open_preferences(self):
        self.preferences_manager.open_preferences(self.root, self.update_pagination, self.load_page, self.current_page)

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
