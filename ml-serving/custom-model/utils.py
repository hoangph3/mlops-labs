import numpy as np
import matplotlib.pyplot as plt
import matplotlib  


matplotlib.rcParams.update({'font.size': 22})

def plot(inputs, labels, predictions=None):
    # Get the images, labels, and optionally predictions
    batch_size = len(inputs)
    if predictions is None:
        predictions = batch_size * [None]

    # Configure the layout of the grid
    x = int(np.ceil(np.sqrt(batch_size)))
    y = int(np.ceil(batch_size / x))
    fig = plt.figure(figsize=(x * 6, y * 7))

    for i, (image, label, prediction) in enumerate(zip(inputs, labels, predictions)):
        # Render the image
        ax = fig.add_subplot(x, y, i+1)
        ax.imshow(image, aspect='auto')
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])

        # Display the label and optionally prediction
        x_label = 'Label: {}'.format(label)
        if prediction is not None:
            x_label = 'Prediction: {}\n'.format(prediction) + x_label
            ax.xaxis.label.set_color('green' if label == prediction else 'red')
            ax.set_xlabel(x_label)

    plt.savefig("images/predictions.png")
