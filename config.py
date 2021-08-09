import os

DATA_DIR = "./data/"

INSTANCES = [
    "sh-patrik",
    "sh-vit",
    "collage-jakub",
    "collage-premek",
    "legacy-franta-tomas",
    "legacy-tereza"
]

DIR_NAMES = {
    "actions": "actions",
    "results": "results",
    # "queries": "queries",
    "requests": "eval-server-requests",
    "summary": "summary"
    
}

THUMBS_DIR = "./thumbs/"
THUMBS_LIST_DIR = DATA_DIR + "thumbs.txt"

OUT_DIRS = {
    "dres": "./out/dres"
}

TASKS_JSON = os.path.join(DATA_DIR, "tasks.json")
TASKS_STARTS = os.path.join(DATA_DIR, "eval-server-tasks-starts.csv")
TASK_MAPPING = os.path.join(DATA_DIR, "mediaItems.csv")

def path(name):
    if (name in INSTANCES):
        return os.path.join(DATA_DIR, name)
    else:
        raise Exception("Uknown name!")

def name(instance_idx):
    return INSTANCES[instance_idx]

def dir_names():
    return DIR_NAMES

def out_dir(name):
    return OUT_DIRS[name]      

def thumbs_dir():
    return THUMBS_DIR     

def thumbs_list_filepath():
    return THUMBS_LIST_DIR     