from pathlib import Path
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input
import tensorflow as tf
import pandas as pd
import argparse
import pickle


def build_model(input_shape):
    input_layer = Input(shape=(input_shape,))
    first_dense = Dense(units='128', activation='relu')(input_layer)
    second_dense = Dense(units='128', activation='relu')(first_dense)

    # Y1 output will be fed directly from the second dense
    y1_output = Dense(units='1', name='y1_output')(second_dense)
    third_dense = Dense(units='64', activation='relu')(second_dense)

    # Y2 output will come via the third dense
    y2_output = Dense(units='1', name='y2_output')(third_dense)

    # Define the model with the input layer and a list of output layers
    model = Model(inputs=input_layer, outputs=[y1_output, y2_output])
    print(model.summary())

    return model


def main(args):
    norm_train_X = pd.read_csv(args.input_train_x)
    with open(args.input_train_y, "rb") as file:
        train_Y = pickle.load(file)

    input_shape = len(norm_train_X.columns)
    model = build_model(input_shape)
    optimizer = tf.keras.optimizers.SGD(learning_rate=args.learning_rate)
    model.compile(optimizer=optimizer,
                  loss={'y1_output': 'mse', 'y2_output': 'mse'},
                  metrics={'y1_output': tf.keras.metrics.RootMeanSquaredError(),
                          'y2_output': tf.keras.metrics.RootMeanSquaredError()})

    history = model.fit(norm_train_X, train_Y, epochs=args.epochs, batch_size=args.batch_size)

    Path(args.output_model).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_history).parent.mkdir(parents=True, exist_ok=True)

    model.save(args.output_model)
    with open(args.output_history, "wb") as file:
        train_Y = pickle.dump(history.history, file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalize dataset')
    parser.add_argument('--input_train_x', type=str, help='train features')
    parser.add_argument('--input_train_y', type=str, help='train labels')
    parser.add_argument('--learning_rate', type=float, help='learning rate')
    parser.add_argument('--epochs', type=int, help='number of epochs')
    parser.add_argument('--batch_size', type=int, help='batch size')

    parser.add_argument('--output_model', type=str, help='model checkpoint')
    parser.add_argument('--output_history', type=str, help='prediction result')

    args = parser.parse_args()
    main(args)