#!/usr/bin/env python
from os import path
from PIL import Image
import numpy as np
from wordcloud import WordCloud
import pickle

def open_binary_file_to_write(filename):
    try: return open(filename, "wb+")
    except:
        return None

def open_binary_file_to_read(filename):
    try: return open(filename, "rb")
    except:
        return None

class WordCloudGenerator():
    def __init__(self, keyworddict):
        self._keyworddict = keyworddict
        d = path.dirname(__file__)
        self._mask = np.array(Image.open(path.join(d, "word_cloud_mask.png")))

    def generate_word_cloud(self):
        d = path.dirname(__file__)
        font_url = path.join(d, "DroidSansMono.ttf")
        #wc = WordCloud(font_path=font_url, width=1640, height=624, background_color="white", max_words=300, scale=0.5) #fb cover
        #wc = WordCloud(font_path=font_url, width=1200, height=630, background_color="white", max_words=300, scale=0.5) #fb post
        wc = WordCloud(font_path=font_url, width=1200, height=630, background_color="white", max_words=300, scale=0.5, mask=self._mask) #fb post
        wc.generate_from_frequencies(self._keyworddict)

        wc.to_file(path.join(d, "word_cloud.png"))

# tao word cloud image

print("Dang tao word cloud voi tag list")
with open_binary_file_to_read("tag_dict.dat") as stream:
    tag_dict = pickle.load(stream)
    WordCloudGenerator(tag_dict).generate_word_cloud() # save word cloud to word_cloud.png
