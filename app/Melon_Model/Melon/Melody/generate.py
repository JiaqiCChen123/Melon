import os
import re
import time
import string
import numpy as np
from music21 import *
# import tensorflow as tf
import matplotlib.pyplot as plt
from midi2audio import FluidSynth
from gensim.models import Word2Vec
from hyphenate import hyphenate_word
from matplotlib.patches import Polygon
from sklearn.neighbors import KernelDensity

import utils, midi_statistics
from Melon_Model.Melon.Harmonization.music_transformer import *
from Melon_Model.Melon.Harmonization.multitask_transformer import *
# from app.yylab1Release1 import utils, midi_statistics
# from app.yylab1Release1.Melon.Harmonization.music_transformer import *
# from app.yylab1Release1.Melon.Harmonization.multitask_transformer import *

# basedir = os.path.abspath(os.path.dirname(__file__))

# def create_syllable(lyrics):
#     '''
#     written by Yunzheng, this function will strip the punctuations in the given text,
#     and generate syllables as the model input format.
#     It's not perfect because some syllables and not detected as I'm using the pkg called 'hyphenate',
#     which is a little different from syllable detection
#     '''
#     regex = re.compile('[' + re.escape(string.punctuation) + '0-9\\r\\t\\n]')
#     lyrics = regex.sub("", lyrics)
#     lyrics = lyrics.split()

#     combinations = [[] for i in range(len(lyrics))]
#     for ly_ind in range(len(lyrics)):
#         combinations[ly_ind].append(hyphenate_word(lyrics[ly_ind]))
#         combinations[ly_ind].append(lyrics[ly_ind])

#     res = []
#     for pair in combinations:
#         for syllable in pair[0]:
#             res.append([syllable, pair[1]])
#     return res

# def model(syll_model_path, word_model_path, model_path, lyrics):
#     syllModel = Word2Vec.load(syll_model_path)
#     wordModel = Word2Vec.load(word_model_path)
#     length_song = len(lyrics)
#     cond = []

#     for i in range(20):
#         if i < length_song:
#             syll2Vec = syllModel.wv[lyrics[i][0]]
#             word2Vec = wordModel.wv[lyrics[i][1]]
#             cond.append(np.concatenate((syll2Vec, word2Vec)))
#         else:
#             cond.append(np.concatenate((syll2Vec, word2Vec)))

#     flattened_cond = []
#     for x in cond:
#         for y in x:
#             flattened_cond.append(y)
#     model_path = basedir + '/saved_gan_models/1August/epochs_models/model_epoch395'

#     x_list = []
#     y_list = []

#     with tf.Session(graph=tf.Graph()) as sess:
#         tf.saved_model.loader.load(sess, [], model_path)
#         graph = tf.get_default_graph()
#         keep_prob = graph.get_tensor_by_name("model/keep_prob:0")
#         input_metadata = graph.get_tensor_by_name("model/input_metadata:0")
#         input_songdata = graph.get_tensor_by_name("model/input_data:0")
#         output_midi = graph.get_tensor_by_name("output_midi:0")
#         feed_dict = {}
#         feed_dict[keep_prob.name] = 1.0
#         condition = []
#         feed_dict[input_metadata.name] = condition
#         feed_dict[input_songdata.name] = np.random.uniform(size=(1, 20, 3))
#         condition.append(np.split(np.asarray(flattened_cond), 20))
#         feed_dict[input_metadata.name] = condition
#         generated_features = sess.run(output_midi, feed_dict)
#         sample = [x[0, :] for x in generated_features]
#         sample = midi_statistics.tune_song(utils.discretize(sample))
#         midi_pattern = utils.create_midi_pattern_from_discretized_data(sample[0:length_song])
#         destination = "./app/static/music/test.mid"
#         destination_mp3 = "./app/static/music/test.wav"
#         midi_pattern.write(destination)
#         # fs = FluidSynth()
#         # fs.midi_to_audio(destination, destination_mp3)

#         print('Midi generation done')

# def get_harmonization(midi_file):
#     midi_stream = file2stream(midi_file)
#     midi_key = midi_stream.analyze('key.krumhanslschmuckler')
#     transpose_interval = interval.Interval(midi_key.tonic, pitch.Pitch('C'))
#     inverse_transpose_interval = interval.Interval(pitch.Pitch('C'), midi_key.tonic)
#     print(transpose_interval)
#     midi_stream = midi_stream.transpose(transpose_interval)
#     multitrack_item = MultitrackItem.from_stream(midi_stream, empty_vocab)
#     melody = multitrack_item.melody
#     empty_chords = MusicItem.empty(empty_vocab, seq_type=SEQType.Chords)
#     pred_chord = learner.predict_s2s(input_item=melody, target_item=empty_chords)
#     combined = MultitrackItem(melody, pred_chord)
#     combined = combined
#     return combined.stream.transpose(inverse_transpose_interval)

# def save_mp3(stream_object):
#     out_midi = stream_object.write('midi')
#     # out_wav = str(Path(out_midi).with_suffix('.mp3'))
#     out_wav = "./app/static/music/test.mp3"
#     FluidSynth("./Melon_Model/FluidR3_GM.sf2").midi_to_audio(out_midi, out_wav)
#     return out_wav

# if __name__ == "__main__":
#     lyrics = 'You turn my nights! into days and lead me to mysterious ways'
#     syll_model_path = basedir + '/enc_models/syllEncoding_20190419.bin'
#     word_model_path = basedir + '/enc_models/wordLevelEncoder_20190419.bin'
#     model_path = 'saved_gan_models/1August/epochs_models/model_epoch395'
#     lyrics = create_syllable(lyrics)
#     model(syll_model_path, word_model_path, model_path, lyrics)
#     time.sleep(3)
#     midi_path = Path('./Melon_Model/data/midi/examples')
#     data_path = Path('./Melon_Model/data/')
#     pretrained_url = 'https://ashaw-midi-web-server.s3-us-west-2.amazonaws.com/pretrained/MultitaskSmallKeyC.pth'
#     pretrained_path = data_path/'pretrained'/Path(pretrained_url).name
#     empty_data = MusicDataBunch.from_files([], data_path, processors=[Midi2ItemProcessor()], ignore_empty=True)
#     learner = multitask_model_learner(empty_data, pretrained_path=pretrained_path)
#     empty_vocab = empty_data.vocab
#     output = get_harmonization('./app/static/music/test.mid')
#     save_mp3(output)