import tensorflow as tf
import numpy as np
import argparse
import logging


def build_and_compile_cnn_model():
    model = tf.keras.Sequential([
      tf.keras.Input(shape=(784,)),
      tf.keras.layers.Dense(128, activation='relu'),
      tf.keras.layers.Dense(64, activation='relu'),
      tf.keras.layers.Dense(10)
      ])
    model.compile(
      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
      optimizer=tf.keras.optimizers.SGD(learning_rate=0.001),
      metrics=['accuracy'])
    return model


def _scale(image, label):
    """Scales an image tensor."""
    image = tf.cast(image, tf.float32)
    image /= 255.
    return tf.reshape(image, shape=(784,)), label


def train(args):
    BUFFER_SIZE = 100000
    with np.load(args.data_file) as data:
        train_examples = data['x_train']
        train_labels = data['y_train']
        test_examples = data['x_test']
        test_labels = data['y_test']
    
    train_dataset = tf.data.Dataset.from_tensor_slices((train_examples, train_labels))
    test_dataset = tf.data.Dataset.from_tensor_slices((test_examples, test_labels))

    train_dataset = train_dataset.map(_scale).cache().shuffle(BUFFER_SIZE).batch(args.batch_size)
    test_dataset = test_dataset.map(_scale).cache().shuffle(BUFFER_SIZE).batch(args.batch_size)

    callbacks = [
        tf.keras.callbacks.experimental.BackupAndRestore(args.checkpoint_path)
    ]
    model = build_and_compile_cnn_model()
    model.summary()
    model.fit(train_dataset,
              epochs=args.epochs,
              callbacks=callbacks,
              validation_data=test_dataset
    )
    logging.info("Saving the trained model to: {}".format(args.saved_model_path))
    tf.keras.models.save_model(model, args.saved_model_path)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs',
                        type=int,
                        required=True,
                        help='Number of epochs to train.')
    parser.add_argument('--batch_size',
                        type=int,
                        required=True,
                        help='Batch size to train.')
    parser.add_argument('--saved_model_path',
                        type=str,
                        required=True,
                        help='Tensorflow export directory.')
    parser.add_argument('--checkpoint_path',
                        type=str,
                        required=True,
                        help='Tensorflow checkpoint directory.')
    parser.add_argument('--data_file',
                        type=str,
                        required=True,
                        help='Data file to train and test.')
    args = parser.parse_args()
    train(args)
