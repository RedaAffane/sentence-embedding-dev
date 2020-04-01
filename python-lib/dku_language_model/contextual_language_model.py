# -*- coding: utf-8 -*-
import os
import tensorflow as tf
import tensorflow_hub as hub
from abstract_language_model import AbstractLanguageModel
from language_model_utils import clean_text
import logging
logger = logging.getLogger(__name__)


class ContextualLanguageModel(AbstractLanguageModel):
      
    def __init__(self, model_path):
        AbstractLanguageModel.__init__(self, model_path)
        self.sess = None
    
    
class ElmoModel(ContextualLanguageModel):
    
    @staticmethod
    def get_model_name():
        return 'ELMO pretrained model'
    
    def load_model(self):
        # Set path for loading the pre-trained ELMo model
        os.environ["TFHUB_CACHE_DIR"] = os.path.join(self.model_path)
        logger.info("Initializing ELMo...")
        self.model = hub.KerasLayer("https://tfhub.dev/google/elmo/3", trainable=True)
        # Initialize the model
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())
        self.sess.run(tf.tables_initializer())

    def get_text_batches(self, texts):
        max_sequence_length = 100
        batch_size = 32

        logger.info("Creating text batches for ELMo")
        texts = [' '.join(s.split()[:max_sequence_length]) for s in texts]
        n_texts = len(texts)

        text_batches = ([texts[i * batch_size: (i + 1) * batch_size] for i in range(n_texts // batch_size)]
                        + [texts[(n_texts // batch_size)*batch_size:]])
        return text_batches
    
    def get_sentence_embedding(self, texts):
        cleaned_texts = map(clean_text, texts)
        batches = self.get_text_batches(cleaned_texts)
        embedded_sentences = []
        for batch in batches:
            tensors = self.model(batch, signature="default", as_dict=True)["default"]
            embeddings = self.sess.run(tensors)
            embedded_sentences.extend(embeddings.tolist())
        return embedded_sentences

    def get_weighted_sentence_embedding(self, texts, smoothing_parameter, npc):
        # for contextual embedding, weights are already integrated in the computation
        return self.get_sentence_embedding(texts)

class UniversalSentenceEncoderModel(ContextualLanguageModel):
    
    @staticmethod
    def get_model_name():
        return 'Universal Sentence Encoder model'
    
    def load_model(self):
        # Set path for loading the pre-trained ELMo model
        os.environ["TFHUB_CACHE_DIR"] = os.path.join(self.model_path)
        logger.info("Initializing Universal Sentence Encoder...")
        self.model = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder/4")
    
    def get_sentence_embedding(self, texts):
        cleaned_texts = map(clean_text, texts)
        embedded_sentences = self.model(cleaned_texts)
        return embedded_sentences
        
    def get_weighted_sentence_embedding(self, texts, smoothing_parameter, npc):
        # for contextual embedding, weights are already integrated in the computation
        return self.get_sentence_embedding(texts)