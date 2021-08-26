import numpy as np
import csv
import json
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sb
import shutil

import pprint
pp = pprint.PrettyPrinter(indent=4)

import config
import utils

from constants import *

def move_y(y, off):
    return y + (y * 1.4 * off)

def move_x(x, off, len):
    return x + (len * 0.015 * off)


def plot_mark(plt, x, y, marker_params, o_x=0, o_y=0, len=360, p=False):
    xx = move_x(x, o_x, len)
    yy = move_y(y, o_y)

    if p:
        print(f"{xx}, , {yy}")

    plt.plot([xx], [yy], clip_on=False, **marker_params)

def plot_arrow(plt, x, y, x2, y2, color, o_x=0, o_y=0, len=360):
    xx = move_x(x, o_x, len)
    yy = move_y(y, o_y)

    xx2 = x2 - x
    yy2 = y2 - y

    plt.annotate("", xy=(xx, yy), xytext=(xx2, yy2), textcoords='offset points', rotation=0, size=10,
        horizontalalignment='left', verticalalignment="center", 
        color=color, arrowprops=dict(
            arrowstyle="<|-", 
            alpha=1,
            facecolor=color, 
            edgecolor=color,
            lw=2
        )
    )

# #######################
# VISUAL
# #######################

def plot_relocation_mark(plt, x, y, changed, color, color_c, o_x=0, o_y=0, len=360):
    marker_params = { 
        "marker": r"$I$", 
        "markerfacecolor": color_c if changed else color, 
        "markeredgecolor": color_c if changed else color, 
        "markersize": 10,
        "alpha": 0.5
    }

    w = 20
    xx = x - 3 
    xx2 = x + w

    plot_arrow(plt, xx, y, xx2, y, color_c if changed else color, o_x=0, o_y=0.5, len=360)
    

def plot_canvas_mark(plt, x, y, changed, color, color_c):
    marker_bg = {
        "marker": "s", 
        "markerfacecolor": "#FFFFFF", 
        "markeredgewidth": 2,
        "markeredgecolor": color_c if changed else color, 
        "markersize": 25,
        'linestyle': '-',
        "alpha": 1
    }

    plot_mark(plt, x, y, marker_bg)

# #######################
# CENTER MARK
# #######################

marker_bg = {
    "marker": "o", 
    "markerfacecolor": "#FFFFFF", 
    "markeredgecolor": "#FFFFFF", 
    "markersize": 16,
    "alpha": 0.5,
}

marker_bg_azure = {
    "marker": "o", 
    "markerfacecolor": "#97f3e5", 
    "markeredgecolor": "#FFFFFF", 
    "markersize": 10,
    "alpha": 0.5
}


marker_bg_pink = {
    "marker": "o", 
    "markerfacecolor": "#f397a5", 
    "markeredgecolor": "#FFFFFF", 
    "markersize": 10,
    "alpha": 0.5
}

#
# Mark: INITIAL 
#
def plot_initial_mark(plt, x, y, changed, color, color_c, o_x=0, o_y=0, len=360):
    marker_params = { 
        "marker": r"$I$", 
        "markerfacecolor": color_c if changed else color, 
        "markeredgecolor": color_c if changed else color, 
        "markersize": 10,
        "alpha": 0.9
    }
    #plot_mark(plt, x, y, marker_bg)
    plot_mark(plt, x, y, marker_params, o_x, o_y, len)

#
# Mark: TEXT
#
def plot_text_mark(plt, x, y, changed, color, color_c, o_x=0, o_y=0, len=360):
    marker_params = { 
        "marker": r"$T$", 
        "markerfacecolor": color_c if changed else color, 
        "markeredgecolor": color_c if changed else color, 
        "markersize": 10,
        "alpha": 0.9
    }
    #plot_mark(plt, x, y, marker_bg)
    plot_mark(plt, x, y, marker_params, o_x, o_y, len)

#
# Mark: BITMAP
#
def plot_bitmap_mark(plt, x, y, changed, color, color_c, o_x=0, o_y=0, len=360):
    marker_params = { 
        "marker": r"$B$", 
        "markerfacecolor": color_c if changed else color, 
        "markeredgecolor": color_c if changed else color, 
        "markersize": 10,
        "alpha": 0.9
    }
    #plot_mark(plt, x, y, marker_bg)
    plot_mark(plt, x, y, marker_params, o_x, o_y, len)


#
# Mark: NN
#
def plot_nn_mark(plt, x, y, changed, color, color_c, o_x=0, o_y=0, len=360):
    marker_params = { 
        "marker": r"$N$", 
        "markerfacecolor": color_c if changed else color, 
        "markeredgecolor": color_c if changed else color, 
        "markersize": 10,
        "alpha": 0.9
    }
    #plot_mark(plt, x, y, marker_bg)
    plot_mark(plt, x, y, marker_params, o_x, o_y, len)

# #######################
# TOP-LEFT
# #######################
#
# Mark: TEMPORAL
#
def plot_temporal_mark(plt, x, y, changed, color, color_c, o_x=0, o_y=0, len=360):
    marker_params = { 
        "marker": r"$t$", 
        "markerfacecolor": color_c if changed else color, 
        "markeredgecolor": color_c if changed else color, 
        "markersize": 6,
        "alpha": 0.9
    }
    #plot_mark(plt, x, y, marker_bg_azure, o_x- 0.4, o_y + 0.4)
    plot_mark(plt, x , y , marker_params, o_x- 0.4, o_y + 0.4, len, p=False)

# #######################
# TOP-RIGHT
# #######################
#
# Mark: LIKE
#
def plot_like_mark(plt, x, y, changed, color, color_c, o_x=0, o_y=0, len=360):
    marker_params = { 
        "marker": r"$L$", 
        "markerfacecolor": color_c if changed else color, 
        "markeredgecolor": color_c if changed else color, 
        "markersize": 5,
        "alpha": 0.9
    }
    #plot_mark(plt, x, y, marker_bg_pink, o_x + 0.4, o_y + 0.4)
    plot_mark(plt, x , y , marker_params, o_x+ 0.5, o_y - 0.2, len, p=False)
