import os

def rename_images(folder_path, prefix="image"):

    image_extensions = ('.png')

    # List all files in the folder
    files = os.listdir(folder_path)

    # Filter image files
    image_files = [f for f in files if f.lower().endswith(image_extensions)]

    # Sort files (optional, for consistent ordering)
    image_files.sort()

    # Rename each image
    for index, filename in enumerate(image_files, start=1):
        ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}_{index}{ext}"
        src = os.path.join(folder_path, filename)
        dst = os.path.join(folder_path, new_name)
        os.rename(src, dst)
        print(f"Renamed: {filename} → {new_name}")

# Example usage
folder = "./images"
rename_images(folder)

