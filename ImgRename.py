#!/usr/bin/env python3
import os
import random
import sys
import argparse
from termcolor import colored
from tqdm import tqdm

SCRIPT_VERSION = "3.2"

from checkVersion import check_version
check_version(SCRIPT_VERSION)



IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".avif", ".webm", ".bmp", ".tiff", ".gif", ".webp"}
CAMERA_MODELS = [
    "DSC0",
    "IMGP",
    "CIMG",
    "GOPR",
    "DSCF",
    "DJI_",
    "SEMC",
    "DUW",
    "IMGP"
    "MGP"
    "S700",
    "RICOH_",
    "SIPIX",
    "BENQ",
    "D47M"
    "JD"
    "KIF_"
    "SANY"
    "moto",
    "D47M",
    "HPIM",
    "IMAG",
    "PICT",
    "DCM",
    "DSC",
    "PXL_",
    "SAM_",
    "B000",
    "IMG_",
    "DSC_",
    "100CANON",
    "101ND800",
    "100APPLE",
    "_DSC",
    "GX",
    "DSCN"
]

def print_colored(message, color="cyan"):
    print(colored(message, color))

def is_image_file(filename):
    return any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)

def find_images_in_directory(directory):
    images = []
    for root, _, files in os.walk(directory):
        for file in files:
            if is_image_file(file):
                images.append(os.path.join(root, file))
    return images

def rename_images(images, camera_model):
    start_number = random.randint(1337, 99999999)
    renamed_count = 0

    for i, image_path in enumerate(tqdm(images, desc="Renaming images")):
        try:
            ext = os.path.splitext(image_path)[1]
            new_name = f"{camera_model}_{start_number + i}{ext}"
            new_path = os.path.join(os.path.dirname(image_path), new_name)
            os.rename(image_path, new_path)
            renamed_count += 1
        except Exception as e:
            print_colored(f"Failed to rename {image_path}: {e}", "red")

    return renamed_count

def main():
    parser = argparse.ArgumentParser(description="Image Rename Tool")
    parser.add_argument('--parent', action='store_true', help='Use the directory name instead of a camera model. Spaces in directory name are replaced with "."')
    args = parser.parse_args()
    use_parent = args.parent

    # --- Splash Message ---
    print_colored("=" * 50, "cyan")
    print_colored("       Image Rename       ", "green")
    print_colored("       Version: 3.2                   ", "green")
    print_colored("       Build Date: June 11, 2026        ", "green")
    print_colored("       Release Notes:        ", "blue")
    print_colored("       Fixed Naming Conventions        ", "blue")
    print_colored("       Added --parent option        ", "blue")
    print_colored("=" * 50, "cyan")
    # ----------------------

    print_colored("Image Rename Tool by noarche | Release Date: December 22 2024", "green")
    print_colored("This tool will rename images in directories to known DSLR naming conventions.", "blue")
    camera_models_copy = CAMERA_MODELS.copy()

    while True:
        directory = input(colored("Enter the directory to process (or 'e' to exit): ", "yellow")).strip()
        if directory.lower() in {'e', 'exit'}:
            print_colored("Exiting the script. Goodbye!", "red")
            sys.exit()

        if not os.path.isdir(directory):
            print_colored("The provided path is not a valid directory. Please try again.", "red")
            continue

        # Get the list of all subdirectories
        directories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
        if not directories:
            print_colored("No subdirectories found in the provided directory.", "red")
            continue

        print_colored(f"Found {len(directories)} subdirectories.", "blue")

        # Shuffle camera models if there are multiple directories
        random.shuffle(camera_models_copy)

        # If there are more directories than camera models, reuse models
        if len(directories) > len(camera_models_copy):
            camera_models_copy = CAMERA_MODELS * (len(directories) // len(CAMERA_MODELS) + 1)
            random.shuffle(camera_models_copy)

        for subdirectory in directories:
            subdirectory_path = os.path.join(directory, subdirectory)
            images = find_images_in_directory(subdirectory_path)
            if not images:
                print_colored(f"No images found in {subdirectory}.", "red")
                continue

            if use_parent:
                camera_model = subdirectory.replace(" ", ".")
                print_colored(f"Using directory name: {camera_model} for {subdirectory}", "magenta")
            else:
                # Assign a different camera model to each directory
                camera_model = camera_models_copy.pop()
                print_colored(f"Using camera model: {camera_model} for {subdirectory}", "magenta")

            renamed_count = rename_images(images, camera_model)
            print_colored(f"Renamed {renamed_count}/{len(images)} images successfully in {subdirectory}.", "green")

        continue_choice = input(colored("Do you want to process another directory? (y/n): ", "yellow"))
        if continue_choice.lower() not in {"y", "yes"}:
            print_colored("Exiting the script. Goodbye!", "green")
            break

if __name__ == "__main__":
    main()
