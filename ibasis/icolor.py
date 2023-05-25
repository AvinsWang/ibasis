import random
import seaborn as sns
from colormap import hex2rgb

sns_color_key = list(sns.xkcd_rgb.keys())

import numpy as np


IDX_COLORS_BGR = [
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 255, 0),
    (255, 128, 0),
    (128, 0, 255),
    (255, 0, 128),
    (0, 128, 255),
    (0, 255, 128),
    (128, 255, 255),
    (255, 128, 255),
    (255, 255, 128),
    (60, 180, 0),
    (180, 60, 0),
    (0, 60, 180),
    (0, 180, 60),
    (60, 0, 180),
    (180, 0, 60),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 255, 0),
    (255, 128, 0),
    (128, 0, 255),
]
LEN_IDX_COLOR = len(IDX_COLORS_BGR)

palette=[]
for i in range(256):
    palette.extend((i,i,i))
palette[:3*21]=np.array([[0, 0, 0],
                         [128, 0, 0],
                         [0, 128, 0],
                         [128, 128, 0],
                         [0, 0, 128],
                         [128, 0, 128],
                         [0, 128, 128],
                         [128, 128, 128],
                         [64, 0, 0],
                         [192, 0, 0],
                         [64, 128, 0],
                         [192, 128, 0],
                         [64, 0, 128],
                         [192, 0, 128],
                         [64, 128, 128],
                         [192, 128, 128],
                         [0, 64, 0],
                         [128, 64, 0],
                         [0, 192, 0],
                         [128, 192, 0],
                         [0, 64, 128]
                         ], dtype='uint8').flatten()


def get_idx_color(idx, mode='bgr', offset=0, exclude=None):
    def _get(c_idx, mode):
        idx = (c_idx) % LEN_IDX_COLOR
        color = IDX_COLORS_BGR[idx]
        if mode == 'rgb':
            color = color[::-1]
        return color
    
    color = _get(idx+offset, mode)
    if exclude:
        if color == exclude:
            color = _get(idx+offset+1, mode)
    return color


def get_random_color(type='bgr'):
    i = random.randint(0, len(sns_color_key) - 1)
    hex_color = sns.xkcd_rgb[sns_color_key[i]]
    rgb_color = list(hex2rgb(hex_color))
    if type == 'rgb':
        return rgb_color
    else:
        bgr_color = rgb_color[::-1]
        return bgr_color
