import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
from main import find_duplicates


def on_find_duplicates_complete(duplicates):
    """
    Callback function to handle the result of the duplicate finding process.

    Args:
        duplicates (list): A list of tuples containing paths of duplicate images.

    Returns:
        None
    """
    # Clear previous grid content
    for widget in result_frame.winfo_children():
        widget.destroy()

    # Create a set to track unique duplicate groups
    unique_duplicates = set()

    for dup in duplicates:
        # Use a tuple of sorted paths to ensure uniqueness
        unique_duplicates.add(tuple(sorted(dup)))

    # Convert the set back to a list
    unique_duplicates = list(unique_duplicates)

    # Insert headers
    headers = ['Index', 'Duplicate 1', 'Duplicate 2', 'Action 1', 'Action 2']
    for col, header in enumerate(headers):
        header_label = tk.Label(result_frame, text=header, borderwidth=2, relief='solid', padx=10, pady=10)
        header_label.grid(row=0, column=col, sticky='nsew')

    for idx, dup in enumerate(unique_duplicates):
        (tk.Label(result_frame, text=idx + 1, borderwidth=2, relief='solid', padx=10, pady=10)
         .grid(row=idx + 1, column=0, sticky='nsew'))
        # Duplicate paths
        (tk.Label(result_frame, text=dup[0], borderwidth=2, relief='solid', padx=10, pady=10)
         .grid(row=idx + 1, column=1, sticky='nsew'))
        (tk.Label(result_frame, text=dup[1], borderwidth=2, relief='solid', padx=10, pady=10)
         .grid(row=idx + 1, column=2, sticky='nsew'))
        # Buttons
        delete_button = tk.Button(
            result_frame,
            text="Delete",
            command=lambda path=dup[1]: delete_image(path),
            padx=10,
            pady=10
        )
        view_button = tk.Button(
            result_frame,
            text="View",
            command=lambda path=dup[1]: view_image(path),
            padx=10,
            pady=10
        )
        delete_button.grid(row=idx + 1, column=3, sticky='ew')
        view_button.grid(row=idx + 1, column=4, sticky='ew')

    duplicates_found.config(text=f"Duplicates found: {len(duplicates)}")
    if not duplicates:
        messagebox.showinfo("No Duplicates", "No duplicates found.")

    # Reset progress and UI state
    progress_bar['value'] = 0
    progress_label.config(text="0/0 images")
    select_button.config(state=tk.NORMAL)  # Re-enable the button


def update_progress(current, total, progress):
    """
    Updates the progress bar and label during the image processing.

    Args:
        current (int): The current number of processed images.
        total (int): The total number of images.
        progress (float): The progress percentage.

    Returns:
        None
    """
    progress_bar['value'] = progress
    progress_label.config(text=f"{current}/{total} images")
    root.update_idletasks()


def delete_image(image_path):
    """
    Deletes the specified image file.

    Args:
        image_path (str): The path to the image to be deleted.

    Returns:
        None
    """
    if messagebox.askyesno("Delete Image", f"Are you sure you want to delete {image_path}?"):
        os.remove(image_path)
        messagebox.showinfo("Deleted", f"Deleted {image_path}")
        select_folder()


def view_image(image_path):
    """
    Opens a new window to view the specified image.

    Args:
        image_path (str): The path to the image to be viewed.

    Returns:
        None
    """
    top = tk.Toplevel(root)
    top.title("View Image")
    img = Image.open(image_path)
    img = ImageTk.PhotoImage(img)
    label = tk.Label(top, image=img)
    label.image = img
    label.pack()


def select_folder():
    """
    Opens a folder selection dialog and starts the duplicate finding process.
    Returns:
        None
    """
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    # Get the tolerance level from the Entry widget
    try:
        tolerance = int(tolerance_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid integer for tolerance.")
        return

    # Disable the button to prevent multiple folder selections
    select_button.config(state=tk.DISABLED)

    # Set progress label to indicate processing
    progress_label.config(text="Processing...")
    root.update_idletasks()

    # Start the find duplicates process in a new thread
    thread = threading.Thread(target=find_duplicates,
                              args=(folder_path, tolerance, update_progress, on_find_duplicates_complete))
    thread.start()


def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# Update scroll region
def update_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))


# Functions for menu items

def show_about():
    messagebox.showinfo("About", "Dupli Pic Finder v0.2.0")


def show_help():
    top = tk.Toplevel(root)
    top.title("Help")

    # Create a Text widget for the help text
    help_text_area = tk.Text(top, height=15, width=90, background="white")
    help_text_area.insert("1.0", "More info on how to use this application...\n\n"
                                 "1. Select Folder: Use this button to choose a folder containing images.\n"
                                 "2. Tolerance Level: Enter the tolerance level for finding duplicates.\n"
                                 "3. Delete: Deletes the selected image from your system.\n"
                                 "4. View: Opens a new window to view the selected image.\n\n"
                                 "For more information, visit https://github.com/timoschneider249/DupliPicFinder")
    help_text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the Text widget
    scrollbar = tk.Scrollbar(top, command=help_text_area.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    help_text_area.config(yscrollcommand=scrollbar.set)


# Set up the main application window
root = tk.Tk()
root.title("Dupli Pic Finder")
root.geometry("1200x800")

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add menus to the menu bar
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Select Folder", command=select_folder)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Help", command=show_help)
help_menu.add_command(label="About", command=show_about)
menu_bar.add_cascade(label="Help", menu=help_menu)

# Create a frame for controls
controls_frame = tk.Frame(root)
controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Add a button to select folder
select_button = tk.Button(controls_frame, text="Select Folder", command=select_folder)
select_button.grid(row=0, column=0, pady=10, padx=(0, 5), sticky='w')

# Add an Entry widget for tolerance level
tolerance_label = tk.Label(controls_frame, text="Tolerance Level:")
tolerance_label.grid(row=0, column=1, pady=10, padx=(5, 0), sticky='w')
tolerance_entry = tk.Entry(controls_frame)
tolerance_entry.grid(row=0, column=2, pady=10, padx=(0, 5), sticky='w')
tolerance_entry.insert(tk.END, "5")

duplicates_found = tk.Label(controls_frame, text="Duplicates found: ")
duplicates_found.grid(row=1, column=0, pady=10, sticky='w')

# Add a progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=1, column=0, pady=10, padx=10, sticky='ew')

# Add a label inside the progress bar
progress_label = tk.Label(root, text="0/0 images", background="white")
progress_label.grid(row=2, column=0, pady=5, padx=10, sticky='w')

# Create a frame for scrollbars and content
frame = tk.Frame(root)
frame.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

# Create canvas and add scrollbars
canvas = tk.Canvas(frame)
x_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
y_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)

# Create a frame inside the canvas to contain the grid of duplicates
result_frame = tk.Frame(canvas)

# Add result_frame to the canvas
canvas.create_window((0, 0), window=result_frame, anchor='nw')

# Configure scrollbars and canvas
canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
x_scrollbar.pack(side='bottom', fill='x')
y_scrollbar.pack(side='right', fill='y')
canvas.pack(side='left', fill='both', expand=True)

# Bind update_scroll_region to the canvas and result_frame
result_frame.bind('<Configure>', update_scroll_region)
canvas.bind('<Configure>', update_scroll_region)
canvas.bind_all("<MouseWheel>", on_mousewheel)

# Make the frame expand with the window size
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)

# Start the GUI event loop
root.mainloop()
