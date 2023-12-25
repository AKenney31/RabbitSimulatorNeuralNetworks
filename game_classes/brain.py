import tensorflow as tf
import keras
from keras import layers
import numpy as np
import os


class Brain:
    def __init__(self, brain=None):
        self.actions = {0: "eat", 1: "drink", 2: "hide", 3: "explore"}
        self.action_chooser = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(3,), name='input_layer'),
            layers.Dense(32, activation='relu', name='hidden_layer'),
            layers.Dense(4, activation='softmax', name='output_layer')
        ])

        self.action_performer = keras.Sequential([
            layers.Dense(8, activation='sigmoid', input_shape=(2,)),
            layers.Dense(2, activation='sigmoid')
        ])
        if brain:
            self.action_chooser.set_weights(brain.action_chooser.weights)
            self.action_performer.set_weights(brain.action_performer.weights)
        else:
            if os.path.exists('./action_chooser_weights.index'):
                self.action_chooser.load_weights('./action_chooser_weights')
                print('loaded action_chooser')
            else:
                for layer in self.action_chooser.layers:
                    layer.set_weights([w + tf.random.normal(w.shape, stddev=.1) for w in layer.get_weights()])
            if os.path.exists('./action_performer_weights.index'):
                self.action_performer.load_weights('./action_performer_weights')
                print('loaded action_performer')
            else:
                for layer in self.action_performer.layers:
                    layer.set_weights([w + tf.random.normal(w.shape, stddev=.1) for w in layer.get_weights()])

    def predict_action(self, inputs):
        inputs = np.expand_dims(inputs, axis=0)  # Add batch dimension
        output = self.action_chooser.predict(inputs)
        return self.actions[int(tf.argmax(output, axis=1).numpy()[0])]

    def predict_new_direction(self, inputs):
        inputs = np.expand_dims(inputs, axis=0)  # Add batch dimension
        output = self.action_performer.predict(inputs)
        return output.flatten()

    def save_action_chooser(self):
        self.action_chooser.save_weights('./action_chooser_weights')

    def save_action_performer(self):
        self.action_performer.save_weights('./action_performer_weights')
