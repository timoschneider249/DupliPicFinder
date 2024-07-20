from PIL import Image
import imagehash
import os


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


def find_duplicates(folder_path, tolerance, progress_callback, complete_callback):
    """
    Finds duplicate images in a given folder based on perceptual hashing.

    Args:
        folder_path (str): The path to the folder containing images.
        tolerance (int): The tolerance level for considering two images as duplicates.
        progress_callback (function): A callback function to update progress.
        complete_callback (function): A callback function to handle the result when processing is complete.

    Returns:
        None
    """
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
              f.lower().endswith(('png', 'jpg', 'jpeg'))]
    total_images = len(images)
    hashes = [None] * total_images

    for i, image in enumerate(images):
        hashes[i] = compute_hash(image)
        # Update GUI progress
        progress = (i + 1) / total_images * 100
        progress_callback(i + 1, total_images, progress)

    duplicates = []
    for i in range(total_images):
        for j in range(i + 1, total_images):
            if hashes[i] and hashes[j] and are_hashes_equal(hashes[i], hashes[j], tolerance):
                duplicates.append((images[i], images[j]))

    complete_callback(duplicates)


if __name__ == "__main__":
    import gui
