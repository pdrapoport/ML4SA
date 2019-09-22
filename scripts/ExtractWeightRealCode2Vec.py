import os
from typing import Tuple

import numpy as np
import tensorflow as tf

from models.Code2VecCustomModel import Code2VecCustomModel


def main() -> None:
    """
    Reads in the original code2vec weights from the original model dir.
    Then creates a Code2VecCustomModel and updates the custom model weights based on the original code2vec weights.
    This model is then saved to disk in the custom model dir such that it can be loaded in the future.
    """
    dirname = os.path.dirname(__file__)
    ORIGINAL_MODEL_DIR = os.path.join(dirname, "..", "resources", "models", "java14m_trainable")
    ORIGINAL_MODEL_NAME = "saved_model_iter8"
    CUSTOM_MODEL_DIR = os.path.join(dirname, "..", "resources", "models", "custom", "custom")
    print(ORIGINAL_MODEL_DIR)
    print(CUSTOM_MODEL_DIR)

    word_vocab, path_vocab, transformer, attention = extract_weights_check_points(ORIGINAL_MODEL_DIR, ORIGINAL_MODEL_NAME)

    model = Code2VecCustomModel()
    model.initialize_variables()

    model.assign_pre_trained_weights(word_vocab, path_vocab, transformer, attention)

    model.save_weights(CUSTOM_MODEL_DIR)


def extract_weights_check_points(model_dir: str, model_name: str, debug: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with tf.compat.v1.Session() as sess:
        # A MetaGraph contains both a TensorFlow GraphDef
        # as well as associated metadata necessary
        # for running computation in a graph when crossing a process boundary.
        saver = tf.compat.v1.train.import_meta_graph(f"{model_dir}\\{model_name}.meta")

        # It will get the latest check point in the directory
        saver.restore(sess, f"{model_dir}\\{model_name}")  # Specific spot

        # Now, let's access and create placeholders variables and
        # create feed-dict to feed new data
        graph = tf.compat.v1.get_default_graph()

        # usefull is you don't know the exact var scope
        if debug:
            for op in graph.get_operations():
                print(op)

        # retrieve vars by name
        word_vocab = sess.run(graph.get_tensor_by_name("model/WORDS_VOCAB:0"))
        path_vocab = sess.run(graph.get_tensor_by_name("model/PATHS_VOCAB:0"))
        transformer = sess.run(graph.get_tensor_by_name("model/TRANSFORM:0"))
        attention = sess.run(graph.get_tensor_by_name("model/ATTENTION:0"))

        return word_vocab, path_vocab, transformer, attention


if __name__ == '__main__':
    main()
