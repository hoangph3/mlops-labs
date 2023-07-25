from mlserver import MLModel
from mlserver.codecs import decode_args
import numpy as np
import tensorflow as tf


# Define a class for our Model, inheriting the MLModel class from MLServer
class Mnist(MLModel):
    # Load the model into memory
    async def load(self) -> bool:
        tf.config.experimental.set_visible_devices([], "GPU")
        self._model = tf.keras.models.load_model("models/latest")
        self._model.summary()
        self.ready = True
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
