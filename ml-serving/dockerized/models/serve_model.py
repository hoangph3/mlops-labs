from mlserver import MLModel
from mlserver.codecs import decode_args
import numpy as np
import tensorflow as tf
import faiss


# Define a class for our Model, inheriting the MLModel class from MLServer
class Mnist(MLModel):
    # Load the model into memory
    async def load(self) -> bool:
        self._model = tf.keras.models.load_model("/mnt/models/latest")
        self._model.summary()
        self.ready = True
        print("Load faiss: {}".format(faiss.__version__))
        return self.ready

    # Logic for making predictions against our model
    @decode_args
    async def predict(self, payload: np.ndarray) -> np.ndarray:
        # convert payload to tf.tensor
        payload_tensor = tf.constant(payload)

        # Make predictions
        predictions = self._model(payload_tensor)
        predictions_max = tf.argmax(predictions, axis=-1)

        # convert predictions to np.ndarray
        response_data = np.array(predictions_max)

        return response_data
