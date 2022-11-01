import tensorflow as tf
import logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepMnist(object):
    def __init__(self):
        self._model = tf.keras.models.load_model("/models/saved_model_dir")

    def predict(self, X, feature_names, meta):
        predictions = self._model(X).numpy()
        return predictions
