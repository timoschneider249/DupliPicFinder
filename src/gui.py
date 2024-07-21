import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading

from src.main import find_duplicates
from src.preferences import PreferencesManager

# Global variables
current_page = 0
items_per_page = 20
total_items = 0
unique_duplicates = []
tolerance = 5  # Default tolerance level

# Callback function
def on_find_duplicates_complete(duplicates):
    global unique_duplicates, total_items
    unique_duplicates = list(set(tuple(sorted(dup)) for dup in duplicates))
    total_items = len(unique_duplicates)
    update_pagination()
    load_page(current_page)


def load_page(page_number):
    start_index = page_number * items_per_page
    end_index = min(start_index + items_per_page, total_items)

    # Clear previous content
    for widget in result_frame.winfo_children():
        widget.destroy()

    # Insert headers
    headers = ['Index', 'Duplicate 1', 'Duplicate 2', 'Action 1', 'Action 2']
    for col, header in enumerate(headers):
        header_label = ctk.CTkLabel(result_frame, text=header)
        header_label.grid(row=0, column=col, sticky='nsew')

    # Load items
    for idx, dup in enumerate(unique_duplicates[start_index:end_index]):
        ctk.CTkLabel(result_frame, text=start_index + idx + 1).grid(row=idx + 1, column=0, sticky='nsew')
        ctk.CTkLabel(result_frame, text=dup[0]).grid(row=idx + 1, column=1, sticky='nsew')
        ctk.CTkLabel(result_frame, text=dup[1]).grid(row=idx + 1, column=2, sticky='nsew')
        delete_button = ctk.CTkButton(result_frame, text="Delete", command=lambda path=dup[1]: delete_image(path))
        view_button = ctk.CTkButton(result_frame, text="View", command=lambda path=dup[1]: view_image(path))
        delete_button.grid(row=idx + 1, column=3, sticky='ew')
        view_button.grid(row=idx + 1, column=4, sticky='ew')

    # Update the layout
    result_frame.update_idletasks()


def update_pagination():
    global current_page
    page_label.configure(text=f"Page {current_page + 1} of {-(total_items // -items_per_page)}")
    prev_button.configure(state=tk.NORMAL if current_page > 0 else tk.DISABLED)
    next_button.configure(state=tk.NORMAL if current_page < (total_items - 1) // items_per_page else tk.DISABLED)


def next_page():
    global current_page
    if current_page < (total_items - 1) // items_per_page:
        current_page += 1
        root.after(0, load_page, current_page)  # Schedule on main thread
        update_pagination()


def prev_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        root.after(0, load_page, current_page)  # Schedule on main thread
        update_pagination()


def update_progress(current, total, progress):
    progress_bar.set(progress)
    progress_label.configure(text=f"{current}/{total} images")
    root.update_idletasks()


def delete_image(image_path):
    if messagebox.askyesno("Delete Image", f"Are you sure you want to delete {image_path}?"):
        os.remove(image_path)
        messagebox.showinfo("Deleted", f"Deleted {image_path}")
        select_folder()


def view_image(image_path):
    top = tk.Toplevel(root)
    top.title("View Image")
    img = Image.open(image_path)
    img = ImageTk.PhotoImage(img)
    label = tk.Label(top, image=img)
    label.image = img
    label.pack()


def select_folder():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return
    global tolerance
    try:
        tolerance = int(tolerance)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid integer for tolerance.")
        return

    select_button.configure(state=tk.DISABLED)
    progress_label.configure(text="Processing...")
    root.update_idletasks()

    thread = threading.Thread(target=find_duplicates,
                              args=(folder_path, tolerance, update_progress, on_find_duplicates_complete))
    thread.start()


def show_about():
    messagebox.showinfo("About", "Dupli Pic Finder v0.3.0")


def show_help():
    top = tk.Toplevel(root)
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


def open_preferences():
    pref_window = tk.Toplevel(root)
    pref_window.title("Preferences")
    pref_frame = ctk.CTkFrame(pref_window)
    pref_frame.pack(padx=10, pady=10)

    tolerance_label = ctk.CTkLabel(pref_frame, text="Tolerance Level:")
    tolerance_label.grid(row=0, column=0, pady=5, sticky='w')
    tolerance_entry = ctk.CTkEntry(pref_frame)
    tolerance_entry.grid(row=0, column=1, pady=5, sticky='w')
    tolerance_entry.insert(0, str(tolerance))

    items_label = ctk.CTkLabel(pref_frame, text="Items Per Page:")
    items_label.grid(row=1, column=0, pady=5, sticky='w')
    items_entry = ctk.CTkEntry(pref_frame)
    items_entry.grid(row=1, column=1, pady=5, sticky='w')
    items_entry.insert(0, str(items_per_page))

    def save_preferences_and_close():
        global items_per_page, tolerance
        try:
            tolerance = int(tolerance_entry.get())
            items_per_page = int(items_entry.get())
            preferences_manager.save_preferences()
            pref_window.destroy()
            update_pagination()
            root.after(0, load_page, current_page)  # Schedule on main thread
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for tolerance and items per page.")

    save_button = ctk.CTkButton(pref_frame, text="Save", command=save_preferences_and_close)
    save_button.grid(row=2, column=0, columnspan=2, pady=10)


# Main window setup
root = ctk.CTk()
root.title("DupliPicFinder")
root.geometry("1200x800")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Select Folder", command=select_folder)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

preferences_menu = tk.Menu(menu_bar, tearoff=0)
preferences_menu.add_command(label="Preferences", command=open_preferences)
menu_bar.add_cascade(label="Preferences", menu=preferences_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Help", command=show_help)
help_menu.add_command(label="About", command=show_about)
menu_bar.add_cascade(label="Help", menu=help_menu)

controls_frame = ctk.CTkFrame(root)
controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

select_button = ctk.CTkButton(controls_frame, text="Select Folder", command=select_folder)
select_button.grid(row=0, column=0, pady=10, padx=(0, 5), sticky='w')

progress_bar = ctk.CTkProgressBar(root, width=500)
progress_bar.grid(row=1, column=0, pady=10, padx=10, sticky='ew')

progress_label = ctk.CTkLabel(root, text="0/0 images")
progress_label.grid(row=2, column=0, pady=5, padx=10, sticky='w')

result_frame = ctk.CTkScrollableFrame(root, label_text="Duplicates")
result_frame.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

pagination_frame = ctk.CTkFrame(root)
pagination_frame.grid(row=5, column=0, pady=10, padx=10, sticky='ew')

prev_button = ctk.CTkButton(pagination_frame, text="Previous", command=prev_page)
prev_button.pack(side=tk.LEFT, padx=5)

page_label = ctk.CTkLabel(pagination_frame, text="Page 1")
page_label.pack(side=tk.LEFT, padx=5)

next_button = ctk.CTkButton(pagination_frame, text="Next", command=next_page)
next_button.pack(side=tk.LEFT, padx=5)

preferences_manager = PreferencesManager()
preferences_manager.load_preferences()

root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(4, weight=0)
root.grid_columnconfigure(1, weight=0)

root.mainloop()
