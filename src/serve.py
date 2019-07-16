import music21
import torch

from fastai.distributed import *
from fastai.text.models.transformer import *

import numpy as np

from .fastai_data import *
from .music_transformer import *
from .encode_data import *

import uuid

def default_config(vocab):
    config = tfmerXL_lm_config.copy()
    
    config['pad_idx'] = vocab.pad_idx
    config['bos_idx'] = vocab.bos_idx
    config['sep_idx'] = vocab.sep_idx
    config['transpose_range'] = (0,12)
    config['note_range'] = vocab.note_range
    config['act'] = Activation.GeLU
    # config['act'] = Activation.ReLU

    config['mem_len'] = 512

    config['bs'] = 16
    config['bptt'] = 256
    
    config['d_model'] = 512
    config['vocab_size'] = len(vocab.itos)
    config['d_inner'] = 2048
    config['n_layers'] = 16
    
    config['n_heads'] = 8
    config['d_head'] = 64


    return config

def mlm_config(vocab):
    config = default_config(vocab)
    config['bias'] = True
    config['enc_layers'] = 8
    config['dec_layers'] = 8
    del config['n_layers']
    return config

def load_music_data(path, cache_name, vocab, **kwargs):
    data = MusicDataBunch.load(path=path, cache_name=cache_name, **kwargs, 
                              train_tfms=[to_single_stream], valid_tfms=[to_single_stream])
    data.vocab = vocab
    return data

def load_music_learner(data, config, load_path=None):
    learn = music_model_learner(data, config)
    if load_path:
        state = torch.load(load_path, map_location='cpu')
        get_model(learn.model).load_state_dict(state['model'], strict=False)
    return learn