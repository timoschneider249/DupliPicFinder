# DupliPicFinder
**DupliPicFinder** is a desktop application designed to help you identify and remove duplicate images from a selected folder. Leveraging perceptual hashing, this tool compares images based on their visual content rather than exact pixel matches. It features a user-friendly graphical interface built with Python's Tkinter library and utilizes Pillow (PIL) for image processing.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)



## Features
- **Folder Selection**: Choose the folder you want to scan for duplicate images.
- **Perceptual Hashing**: Efficiently identifies duplicates by comparing perceptual hashes of images.
- **Progress Tracking**: View a progress bar showing the status of the scanning process.
- **Duplicate Management**: Optionally delete duplicate images after confirming the action.

# Installation

## Download
Navigate to the [Releases](https://github.com/timoschneider249/DupliPicFinder/releases) page on GitHub and download the appropriate executable file for your operating system. For Windows, simply download the .exe file and double-click to run.

## From Source 
**1. Clone the Repository**

````shell
git clone https://github.com/timoschneider249/DupliPicFinder.git
cd DupliPicFinder
````

**2. Set Up Python Environment:**

Ensure Python 3.10 or higher is installed. You can download it from [python.org](https://www.python.org/downloads/).

**3. Install Dependencies:**

Install the required Python libraries using pip:
````shell
pip install pillow imagehash tkinter multiprocessing
````

**4. Run the Application**
````shell
python image_utils.py
````

## Requirements
To run this application, you need to have Python 3 installed along with the following Python libraries:
- ``tkinter`` (comes pre-installed with Python)
- ``Pillow`` (for image processing)
- ``imagehash`` (for perceptual hashing)
- ``multiprocessing`` (for parallel processing, part of the Python standard library)

## Usage
**1. Run the application:**
Open the executable file you downloaded or run ``python main.py`` from the command line if using the source code.

**2. Select Folder:**
Click the "Select Folder" button to choose the directory you want to scan for duplicate images.

**3. Handling Duplicates:**
After scanning, the application will list the duplicate images found. You will be prompted to confirm if you want to delete the duplicates. If you agree, the second occurrence of each duplicate image will be deleted.

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/timoschneider249/DupliPicFinder/blob/main/LICENSE) file for details.
