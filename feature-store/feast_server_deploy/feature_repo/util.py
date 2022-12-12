def onehot_encoder(label_id, num_classes):
    label_init = [0] * num_classes
    label_init[label_id] = 1
    return label_init