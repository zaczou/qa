"""Implements an mnemonic-reader model.
https://arxiv.org/pdf/1705.02798.pdf
"""

import tensorflow as tf

from model.alignment import *
from model.base_model import BaseModel
from model.encoding_util import *
from model.memory_answer_pointer import *
from model.rnn_util import *

class MnemonicReader(BaseModel):
    def setup(self):
        super(MnemonicReader, self).setup()
        ctx_dim = 2 * self.options.rnn_size
        # Step 1. Encode the passage and question.
        ctx_dropout = tf.nn.dropout(self.ctx_inputs, self.keep_prob)
        qst_dropout = tf.nn.dropout(self.qst_inputs, self.keep_prob)
        passage_outputs, question_outputs = encode_passage_and_question(
                self.options, ctx_dropout, qst_dropout, self.keep_prob,
                self.sess, self.batch_size, self.use_dropout_placeholder)
        # Step 2. Run alignment on the passage and query to create a new
        # representation for the passage that is query-aware and self-aware.
        alignment = run_alignment(self.options, passage_outputs,
                question_outputs, ctx_dim, self.sq_dataset, self.keep_prob,
                self.batch_size, self.sess, self.use_dropout_placeholder) # size = [batch_size, max_ctx_length, 2 * rnn_size]
        # Step 3. Use a memory-based answer pointer mechanism to get the loss,
        # and start & end span probabilities
        self.loss, self.start_span_probs, self.end_span_probs = \
            memory_answer_pointer(self.options, alignment, question_outputs,
                ctx_dim, self.spn_iterator, self.sq_dataset, self.keep_prob,
                self.sess, self.use_dropout_placeholder)
