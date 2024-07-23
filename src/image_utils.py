# image_utils.py
from PIL import Image
import imagehash
import os


class ImageUtils:
    @staticmethod
    def compute_hash(image_path):
        """
        Computes the perceptual hash of an image.

        Args:
            image_path (str): The file path to the image.

        Returns:
            imagehash.ImageHash: The perceptual hash of the image.
            None: If an error occurs during processing.
        """
        try:
            img = Image.open(image_path)
            img = img.convert("LA").resize((8, 8), Image.LANCZOS)
            return imagehash.phash(img)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None

    @staticmethod
    def are_hashes_equal(hash1, hash2, tolerance):
        """
        Compares two perceptual hashes to determine if they are similar.

        Args:
            hash1 (imagehash.ImageHash): The first image hash.
            hash2 (imagehash.ImageHash): The second image hash.
            tolerance (int): The tolerance level for hash difference.

        Returns:
            bool: True if the hashes are within the tolerance level, False otherwise.
        """
        return abs(hash1 - hash2) < tolerance

    @staticmethod
    def find_duplicates(folder_path: str, tolerance: int, progress_callback, complete_callback):
        """
        Finds duplicate images in a given folder and its subfolders based on perceptual hashing.

        Args:
            folder_path (str): The path to the folder containing images.
            tolerance (int): The tolerance level for considering two images as duplicates.
            progress_callback (function): A callback function to update progress.
            complete_callback (function): A callback function to handle the result when processing is complete.

        Returns:
            None
        """
        images = []

        # Traverse directory tree
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('png', 'jpg', 'jpeg')):
                    images.append(os.path.join(root, file))

        total_images = len(images)
        if total_images == 0:
            complete_callback([])
            return

        hashes = [None] * total_images

        # Compute hashes for all images
        for i, image in enumerate(images):
            try:
                hash_value = ImageUtils.compute_hash(image)
                if hash_value is not None:
                    hashes[i] = hash_value
                else:
                    print(f"Warning: Unable to compute hash for image {image}")
            except Exception as e:
                print(f"Error processing image {image}: {e}")
            # Update progress
            progress = (i + 1) / total_images * 100
            progress_callback(i + 1, total_images, progress)

        # Filter out None values and their corresponding image paths
        valid_hashes = [(hashes[i], images[i]) for i in range(total_images) if hashes[i] is not None]

        duplicates = []

        # Find duplicates
        for i in range(len(valid_hashes)):
            for j in range(i + 1, len(valid_hashes)):
                hash1, img1 = valid_hashes[i]
                hash2, img2 = valid_hashes[j]
                if ImageUtils.are_hashes_equal(hash1, hash2, tolerance):
                    duplicates.append((img1, img2))

        # Call the complete callback with the duplicates found
        complete_callback(duplicates)
