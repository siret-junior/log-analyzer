import os
import pickle
import datetime
from IPython.display import Image, display, HTML
import shutil

def save_obj(filepath, obj):
    dir = os.path.dirname(filepath)
    os.makedirs(dir, exist_ok=True)

    with open( filepath, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(filepath ):
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def make_html(src):
     return '<img src="{}" style="max-width:100px;display:inline;margin:1px"/>'.format(src)

def print_images_row(images):

    s = ""
    for x in images:
        s += make_html(x)

    display(HTML(s))


def UNIX_from_datetime(dtstr):
    """
    INPUT: 2021-06-21T14:10:58.765
    """
    
    y = int(dtstr[0:4])
    m = int(dtstr[5:7])
    d = int(dtstr[8:10])
    h = int(dtstr[11:13])
    mins = int(dtstr[14:16])
    secs = int(dtstr[17:19])
    us = int(dtstr[20:23]) * 1000
    
    #print(y,m,d,h,mins,secs, us)
    
    return int(datetime.datetime(y, m, d, h, mins, secs, us).timestamp() * 1000)


def from_UNIX(ts, fmt='%d-%m-%Y %H:%M:%S'):
    return datetime.datetime.fromtimestamp(ts / 1000).strftime(fmt)

def find_task_def(json, name):
    for t in json:
        if (t["name"] == name):
            return t

    return None