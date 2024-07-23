from gui import DupliPicFinderApp
import customtkinter as ctk


def main():
    root = ctk.CTk()  # Initialize the main window using customtkinter
    app = DupliPicFinderApp(root)  # Create an instance of the application
    root.mainloop()  # Start the Tkinter event loop


if __name__ == "__main__":
    main()
