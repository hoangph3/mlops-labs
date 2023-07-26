import logging
import idx2numpy

import tensorflow_datasets as tfds
import tensorflow as tf
from model import build_and_compile_cnn_model


def _scale(image, label):
    """Scales an image tensor."""
    image = tf.cast(image, tf.float32)
    image /= 255
    return image, label


def _load_ds(batch_size):
    images = idx2numpy.convert_from_file("./data/train-images-idx3-ubyte")
    labels = idx2numpy.convert_from_file("./data/train-labels-idx1-ubyte")
    dataset = tf.data.Dataset.from_tensor_slices((images, labels))
    dataset = dataset.map(_scale).cache().batch(batch_size).repeat()
    return dataset


def train(epochs, batch_size, steps_per_epoch, saved_model_path):
    """Trains a MNIST classification model using multi-worker mirrored strategy."""
    dataset = _load_ds(batch_size)

    model = build_and_compile_cnn_model()

    model.fit(dataset, epochs=epochs, steps_per_epoch=steps_per_epoch)

    logging.info("Saving the trained model to: {}".format(saved_model_path))
    model.save(saved_model_path)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    tfds.disable_progress_bar()
    train(
        epochs=20,
        batch_size=128,
        steps_per_epoch=100,
        saved_model_path="./models/latest"
    )
