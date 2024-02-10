from main import *


def test_images_exist():
    directory = "tested_images/"
    images_data = get_images(directory)
    assert len(images_data) != 0


def test_file_exists():
    directory = ""
    key_path = directory + "key.bin"
    assert not file_exists(key_path)
    Path(key_path).touch()
    assert file_exists(key_path)
    Path(key_path).unlink()
    assert not file_exists(key_path)


def test_get_images():
    directory = "tested_images/"
    images_data = get_images(directory)
    assert len(images_data) > 0
    imgs_with_exif = 0
    for img_path, img, exif in images_data:
        assert file_exists(img_path)
        assert isinstance(img, np.ndarray)
        assert isinstance(exif, Image.Exif)
        if len(exif.items()) > 0:
            imgs_with_exif += 1
    assert imgs_with_exif > 0


def test_get_key():
    directory = "tested_images/"
    images_data = get_images(directory)
    key = get_key([image for _, image, _ in images_data])
    assert isinstance(key, np.ndarray)
    assert isinstance(key[0], np.uint8)
    assert len(key) == 44236800  # 5120 * 2880 * 3 (star_wars.jpg)
    assert key[0] in range(256)
    

def test_xor():
    img = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]], dtype=np.uint8)
    key = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.uint8)
    xored_img = xor(img, key)
    assert np.array_equal(xored_img, np.array([[1, 3, 1], [7, 1, 3], [1, 15, 1]], dtype=np.uint8))


def test_cypher_decypher():
    directory = "tested_images/"
    images_data = get_images(directory)

    cypher_images(directory)

    cyphered_images_data = get_images(directory)
    for i in range(len(images_data)):
        assert images_data[i][0] == cyphered_images_data[i][0]
        assert not np.array_equal(images_data[i][1], cyphered_images_data[i][1])
        assert images_data[i][2] == cyphered_images_data[i][2]  # exif does not change

    decypher_images(directory)

    decyphered_images_data = get_images(directory)
    for i in range(len(images_data)):
        assert images_data[i][0] == decyphered_images_data[i][0]
        # assert np.array_equal(images_data[i][1], decyphered_images_data[i][1])
        assert images_data[i][1].shape == decyphered_images_data[i][1].shape
        n_of_diff_pixels = np.count_nonzero(images_data[i][1] != decyphered_images_data[i][1])
        print(n_of_diff_pixels)
        assert images_data[i][2] == decyphered_images_data[i][2]
