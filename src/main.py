import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image
import imagehash
import os
import threading


def compute_hash(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert("L").resize((8, 8), Image.LANCZOS)  # Convert to grayscale and resize
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None


def are_hashes_equal(hash1, hash2, tolerance):
    return abs(hash1 - hash2) < tolerance  # Tolerance level for hash difference


def find_duplicates(folder_path, tolerance, callback):
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
              f.lower().endswith(('png', 'jpg', 'jpeg'))]
    total_images = len(images)
    hashes = [None] * total_images

    # Compute hashes in a separate thread
    for i, image in enumerate(images):
        hashes[i] = compute_hash(image)
        progress = (i + 1) / total_images * 100
        progress_bar['value'] = progress
        progress_label.config(text=f"{i + 1}/{total_images} images")
        root.update_idletasks()

    duplicates = []
    for i in range(total_images):
        for j in range(i + 1, total_images):
            if hashes[i] and hashes[j] and are_hashes_equal(hashes[i], hashes[j], tolerance):
                duplicates.append((images[i], images[j]))

    callback(duplicates)


def on_find_duplicates_complete(duplicates):
    # Clear previous text and display new duplicates
    result_text = "Found duplicates:\n"
    for dup in duplicates:
        result_text += f"{dup[0]} == {dup[1]}\n"

    if duplicates:
        result_text += "\nDo you want to delete duplicates?"

        # Show the results in a Text widget
        result_text_widget.delete(1.0, tk.END)  # Clear previous content
        result_text_widget.insert(tk.END, result_text)  # Insert new content

        # Enable the Copy button
        copy_button.config(state=tk.NORMAL)

        # Ask if the user wants to delete duplicates
        if messagebox.askyesno("Duplicates Found", "Do you want to delete duplicates?"):
            for dup in duplicates:
                os.remove(dup[1])  # Delete the second duplicate image
            messagebox.showinfo("Deletion Complete", "Duplicate images have been deleted.")
    else:
        result_text_widget.delete(1.0, tk.END)  # Clear previous content
        result_text_widget.insert(tk.END, "No duplicates found.")

    # Reset progress and UI state
    progress_bar['value'] = 0
    progress_label.config(text="0/0 images")
    select_button.config(state=tk.NORMAL)  # Re-enable the button


def copy_to_clipboard():
    # Copy the content of the Text widget to the clipboard
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(result_text_widget.get(1.0, tk.END))  # Append the content
    root.update()  # Update the clipboard


def select_folder():
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
    threading.Thread(target=find_duplicates, args=(folder_path, tolerance, on_find_duplicates_complete), daemon=True).start()


# Set up the main application window
root = tk.Tk()
root.title("Dupli Pic Finder")
root.geometry("600x500")

# Add a button to select folder
select_button = tk.Button(root, text="Select Folder", command=select_folder)
select_button.pack(pady=10)

# Add a progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(pady=10)

# Add a label inside the progress bar
progress_label = tk.Label(root, text="0/0 images", background="white")
progress_label.pack(pady=5)

# Add a Text widget to display results
result_text_widget = tk.Text(root, wrap=tk.WORD, height=10, width=70)
result_text_widget.pack(pady=10)

# Add a button to copy the results
copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard, state=tk.DISABLED)
copy_button.pack(pady=10)

# Add an Entry widget for tolerance level
tolerance_label = tk.Label(root, text="Enter Tolerance Level:")
tolerance_label.pack(pady=5)
tolerance_entry = tk.Entry(root)
tolerance_entry.pack(pady=5)
tolerance_entry.insert(tk.END, "5")  # Default tolerance value

# Start the GUI event loop
root.mainloop()
