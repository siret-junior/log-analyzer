import os
import pickle
import datetime
from IPython.display import Image, display, HTML
import shutil
import config
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

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

def generate_catype(cats, types):
    return ".".join(sorted(cats)) + "__" + ".".join(sorted(types))


def catype_to_features(catype):
    if not (catype in config.catypes_to_features()):
        raise Exception("Catype does not exist!")
    
    return config.catypes_to_features(catype)

def extract_text_query(text):
    if not (text.startswith("|results|")):
        return None
    
    t = text[9:]
    i = t.find(";")
    
    t = t[0:i]
    
    xx = [x.strip() for x in t.split(">>")]
    return xx


def determine_submit_result(r):
    c = None

    if (r["response"] == None):
        c = "TIMEOUT"
    elif (r["response_code"] == 404):
        c = "SERVER_LAG"
    elif (r["response_code"] == 401):
        c = "LOGGED_OUT"
    elif (r["response_code"] == 412):
        c = "F"
    elif ("submission" in r["response"]):
            
            if (r["response"]["submission"] == "CORRECT"):
                c = "T"
            elif (r["response"]["submission"] == "INDETERMINATE"):
                c = "I"
            else:
                c = "F"

    return c


def cache_index_get(team_name):
    cache_indexf_fpth = config.cache_index_file()
    cache_index = None
    with open(cache_indexf_fpth) as ifs:
        cache_index = json.load(ifs)

    return team_name in cache_index and cache_index[team_name]


def cache_index_set(team_name):
    cache_indexf_fpth = config.cache_index_file()
    cache_index = None
    with open(cache_indexf_fpth) as ifs:
        cache_index = json.load(ifs)

    cache_index[team_name] = True

    with open(cache_indexf_fpth, "w") as ofs:
        str = json.dumps(cache_index)
        ofs.write(str)