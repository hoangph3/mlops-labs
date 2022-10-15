import tensorflow as tf


def false_positive(y_true, y_pred):
    pairwise_dist = _pairwise_distances(y_pred)

    # get positive distace
    mask_anchor_positive = _get_anchor_positive_triplet_mask(y_true)
    anchor_positive_dist = tf.multiply(mask_anchor_positive, pairwise_dist)

    # compute threshold
    threshold = tf.reduce_sum(anchor_positive_dist) / tf.reduce_sum(mask_anchor_positive)

    # get negative distance
    mask_anchor_negative = _get_anchor_negative_triplet_mask(y_true)
    anchor_negative_dist = pairwise_dist + 2 * threshold * (1.0 - mask_anchor_negative)

    # compute fp and fn
    false_positive = tf.reduce_sum(
        tf.cast(anchor_positive_dist > threshold, dtype=tf.float32)
    ) / tf.reduce_sum(mask_anchor_positive)

    false_negative = tf.reduce_sum(
        tf.cast(anchor_negative_dist < threshold, dtype=tf.float32)
    ) / tf.reduce_sum(mask_anchor_negative)

    return tf.cast(false_positive, dtype=tf.float32)


def false_negative(y_true, y_pred):
    pairwise_dist = _pairwise_distances(y_pred)

    # get positive distace
    mask_anchor_positive = _get_anchor_positive_triplet_mask(y_true)
    anchor_positive_dist = tf.multiply(mask_anchor_positive, pairwise_dist)

    # compute threshold
    threshold = tf.reduce_sum(anchor_positive_dist) / tf.reduce_sum(mask_anchor_positive)

    # get negative distance
    mask_anchor_negative = _get_anchor_negative_triplet_mask(y_true)
    anchor_negative_dist = pairwise_dist + 2 * threshold * (1.0 - mask_anchor_negative)

    # compute fp and fn
    false_positive = tf.reduce_sum(tf.cast(anchor_positive_dist > threshold, dtype=tf.float32)) / tf.reduce_sum(mask_anchor_positive)

    false_negative = tf.reduce_sum(
        tf.cast(anchor_negative_dist < threshold, dtype=tf.float32)
    ) / tf.reduce_sum(mask_anchor_negative)

    return tf.cast(false_negative, dtype=tf.float32)


def _pairwise_distances(embeddings, squared=False):
    # Compute the 2D matrix of distances between all the embeddings.
    dot_product = tf.matmul(embeddings, tf.transpose(embeddings))
    square_norm = tf.linalg.diag_part(dot_product)

    distances = tf.expand_dims(square_norm, 1) - 2.0 * dot_product + tf.expand_dims(square_norm, 0)
    distances = tf.maximum(distances, 0.0)

    if not squared:
        mask = tf.cast(tf.equal(distances, 0.0), dtype=tf.float32)
        distances = distances + mask * 1e-16
        distances = tf.sqrt(distances)
        distances = distances * (1.0 - mask)
    return distances


def _get_anchor_positive_triplet_mask(labels):
    # Check that i and j are distinct
    indices_equal = tf.cast(tf.eye(tf.shape(labels)[0]), tf.bool)
    indices_not_equal = tf.logical_not(indices_equal)

    # Check if labels[i] == labels[j]
    # Uses broadcasting where the 1st argument has shape (1, batch_size) and the 2nd (batch_size, 1)
    labels_equal = tf.equal(tf.expand_dims(labels, 0), tf.expand_dims(labels, 1))

    # Combine the two masks
    mask = tf.cast(tf.logical_and(indices_not_equal, labels_equal), dtype=tf.float32)
    return mask


def _get_anchor_negative_triplet_mask(labels):
    # Check if labels[i] != labels[k]
    # Uses broadcasting where the 1st argument has shape (1, batch_size) and the 2nd (batch_size, 1)
    labels_equal = tf.equal(tf.expand_dims(labels, 0), tf.expand_dims(labels, 1))

    mask = tf.cast(tf.logical_not(labels_equal), dtype=tf.float32)
    return mask
