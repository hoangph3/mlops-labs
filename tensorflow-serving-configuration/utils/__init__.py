import matplotlib.pyplot as plt
import tensorflow as tf
import os


from .custom_serving import ServingModule
from .warmup_serving import warmup_serving


def get_image_list(image_dir="images"):
    image_list = [tf.io.read_file(os.path.join(image_dir, image_path))
         for image_path in os.listdir(image_dir)]
    return image_list


def show_image(image_list):
    ncolumns = len(image_list) if len(image_list) < 4 else 4
    nrows = int(len(image_list) // ncolumns)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncolumns, figsize=(10,10))
    for axis, image in zip(axes.flat[0:], image_list):
        decoded_image = tf.image.decode_image(image)
        print(decoded_image.shape)
        axis.set_title(decoded_image.shape)
        axis.imshow(decoded_image.numpy())
    plt.show()
    return


def _decode_and_scale(image, size):
    image = tf.image.decode_image(image, expand_animations=False)
    image_height = image.shape[0]
    image_width = image.shape[1]
    crop_size = tf.minimum(image_height, image_width)
    offset_height = ((image_height - crop_size) + 1) // 2
    offset_width = ((image_width - crop_size) + 1) // 2
    image = tf.image.crop_to_bounding_box(image, offset_height, offset_width, crop_size, crop_size)
    image = tf.cast(tf.image.resize(image, [size, size]), tf.uint8)
    return image


def preprocess_image(raw_images, size):
    preprocessed_images = tf.map_fn(lambda x: _decode_and_scale(x, size), raw_images, dtype=tf.uint8)
    preprocessed_images = tf.image.convert_image_dtype(preprocessed_images, tf.float32)
    return preprocessed_images
