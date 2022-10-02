import tensorflow as tf


LABELS_KEY = 'labels'
PROBABILITIES_KEY = 'probabilities'
NUM_LABELS = 5


class ServingModule(tf.Module):
    """
    A custom tf.Module that adds image preprocessing and output post processing to
    a base TF 2 image classification model from TF Hub. 
    """

    def __init__(self, base_model, input_size, output_labels):
        super(ServingModule, self).__init__()
        self._model = base_model
        self._input_size = input_size
        self._output_labels = tf.constant(output_labels, dtype=tf.string)
        

    def _decode_and_scale(self, raw_image):
        """
        Decodes, crops, and resizes a single raw image.
        """
        
        image = tf.image.decode_image(raw_image, dtype=tf.dtypes.uint8, expand_animations=False)
        image_shape = tf.shape(image)
        image_height = image_shape[0]
        image_width = image_shape[1]
        crop_size = tf.minimum(image_height, image_width)
        offset_height = ((image_height - crop_size) + 1) // 2
        offset_width = ((image_width - crop_size) + 1) // 2
        
        image = tf.image.crop_to_bounding_box(image, offset_height, offset_width, crop_size, crop_size)
        image = tf.image.resize(image, [self._input_size, self._input_size])
        image = tf.cast(image, tf.uint8)
    
        return image
    
    def _preprocess(self, raw_inputs):
        """
        Preprocesses raw inputs as sent by the client.
        """
        
        # A mitigation for https://github.com/tensorflow/tensorflow/issues/28007
        with tf.device('/cpu:0'):
            images = tf.map_fn(self._decode_and_scale, raw_inputs, dtype=tf.uint8)
        images = tf.image.convert_image_dtype(images, tf.float32)
        
        return images
        
    def _postprocess(self, model_outputs):
        """
        Postprocesses outputs returned by the base model.
        """
        
        probabilities = tf.nn.softmax(model_outputs)
        indices = tf.argsort(probabilities, axis=1, direction='DESCENDING')
        
        return {
            LABELS_KEY: tf.gather(self._output_labels, indices, axis=-1)[:,:NUM_LABELS],
            PROBABILITIES_KEY: tf.sort(probabilities, direction='DESCENDING')[:,:NUM_LABELS]
        }
        

    @tf.function(input_signature=[tf.TensorSpec([None, 224, 224, 3], tf.float32)])
    def __call__(self, x):
        """
        A pass-through to the base model.
        """
        
        return self._model(x)

    @tf.function(input_signature=[tf.TensorSpec([None], tf.string)])
    def predict_labels(self, raw_images):
        """
        Preprocesses inputs, calls the base model 
        and postprocesses outputs from the base model.
        """
        
        # Call the preprocessing handler
        images = self._preprocess(raw_images)
        
        # Call the base model
        logits = self._model(images)
        
        # Call the postprocessing handler
        outputs = self._postprocess(logits)
        
        return outputs
