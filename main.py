from PIL import Image
import numpy as np
from pathlib import Path
import cv2


IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp',
                    '.tiff', '.webp', '.raw', '.nef', '.cr2']


def main():
    cypher_images("tested_images/")
    # decypher_images("tested_images/")


def cypher_images(directory: str) -> None:
    """
    Cypheres all images in the directory using the XOR operation with a random key
    """
    key_path = directory + "key.bin"
    if file_exists(key_path):
        print("File with the key (key.bin) already exists in this directory. \nPerhaps images are already cyphered. If not delete the key.bin file")
        return
 
    images_data = get_images(directory)
    key = get_key([image for _, image, _ in images_data])

    for i, (img_path, img, exif) in enumerate(images_data):
        img = xor(img, key)
        img = Image.fromarray(img)
        img.info["exif"] = exif
        img.save(img_path, format="PNG")
        print(f"Image {i + 1}/{len(images_data)} cyphered")
    
    with open(key_path, "wb") as file:
        file.write(key.tobytes())


def decypher_images(directory: str) -> None:
    """
    Decypher all images in the directory using the XOR operation with a key
    from the key.bin file and deletes the key.bin file after decyphering
    """
    key_path = directory + "key.bin"
    if not file_exists(key_path):
        print("File with the key (key.bin) does not exist in this directory.\nPerhaps files are not cyphered")
        return

    images_data = get_images(directory)

    with open(key_path, "rb") as file:
        key = np.fromfile(file, dtype=np.uint8)
    
    for i, (img_path, img, exif) in enumerate(images_data):
        img = xor(img, key)
        img = Image.fromarray(img)
        img.info["exif"] = exif
        img.save(img_path)
        print(f"Image {i + 1}/{len(images_data)} decyphered")

    Path(key_path).unlink()


def file_exists(file_path: str) -> bool:
    file = Path(file_path)
    return file.exists()


def get_images(directory: str) -> list[tuple[str, np.ndarray[np.uint8], dict[str, str]]]:
    """
    Retrieve image data from files in the specified directory.

    Args:
        directory (str): The path to the directory containing image files.

    Returns:
        list[tuple[str, np.ndarray[np.uint8], dict[str, str]]]: A list of tuples, 
        each containing information about an image. Each tuple consists of:
            - The file path of the image (str).
            - The image data represented as a NumPy array of unsigned 8-bit integers (np.ndarray[np.uint8]).
            - A dictionary containing the EXIF metadata of the image (dict[str, str]). 
              If no EXIF data is available, the dictionary will be empty.
    """
    images_data = []
    directory = Path(directory)
    for file in directory.iterdir():
        if file.is_file():
            if file.suffix in IMAGE_EXTENSIONS:
                image = Image.open(file)
                exif = image._getexif()
                if exif is None:
                    exif = {}
                images_data.append((str(file), np.asarray(image), exif))
    return images_data


def get_key(images: list[np.ndarray[np.uint8]]) -> np.ndarray[np.uint8]:
    """
    Returns a key that is 1d array of random numbers from 0 to 255 
    with the length equal to the number of pixels in the largest image
    """
    pixels_count = max(image.size for image in images)
    return np.random.randint(256, size=pixels_count, dtype=np.uint8)


def xor(img: np.ndarray[np.uint8], key: np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
    """
    Cypher/decypher the image using the XOR operation with the key
    """
    key = key[:img.size]
    key = key.reshape(img.shape)
    return img ^ key


if __name__ == '__main__':
    main()