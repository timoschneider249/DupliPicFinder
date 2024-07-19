# DupliPicFinder
This application helps you identify and delete duplicate images in a selected folder. It uses perceptual hashing to compare images and determine similarity. The tool is built using Python's Tkinter library for the graphical user interface (GUI) and Pillow (PIL) for image processing.

## Features
- Select a folder to scan for duplicate images.
- Computes perceptual hashes of images to identify duplicates.
- Provides a progress bar to show the scanning progress.
- Optionally deletes duplicate images after confirmation.

## Requirements
To run this application, you need to have Python 3 installed along with the following Python libraries:
- ``tkinter`` (comes pre-installed with Python)
- ``Pillow`` (for image processing)
- ``imagehash`` (for perceptual hashing)
- ``multiprocessing`` (for parallel processing, part of the Python standard library)

You can install the necessary libraries using pip:
````shell
pip install pillow imagehash
````

## Usage
1. Run the application:
    ````shell
    python main.py
    ````

2. Select Folder:
Click the "Select Folder" button to choose the directory you want to scan for duplicate images.

3. Handling Duplicates:
   After scanning, the application will list the duplicate images found. You will be prompted to confirm if you want to delete the duplicates. If you agree, the second occurrence of each duplicate image will be deleted.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

Feel free to modify or expand the README based on additional features or requirements!
