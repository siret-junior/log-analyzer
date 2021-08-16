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

CACHE_DIR = "./__cache__/"
THUMBS_DIR = "./thumbs/"
THUMBS_LIST_DIR = DATA_DIR + "thumbs.txt"

OUT_DIRS = {
    "dres": "./out/dres",
    "timelines": "./out/timelines"
}

TASKS_JSON = os.path.join(DATA_DIR, "tasks.json")
TASKS_STARTS = os.path.join(DATA_DIR, "eval-server-tasks-starts.csv")
TASK_MAPPING = os.path.join(DATA_DIR, "mediaItems.csv")


FEATURES = {
    "I": "initial",
    "TQ": "text-query",
    "TTQ": "temporal-text-query",
    "LK": "like",
    "TQR": "text-query-relocation",
    "TTQR": "temporal-text-query-relocation",
    "CTQ": "canvas-text-query",
    "TCTQ": "temporal-canvas-text-query",
    "CBQ": "canvas-bitmap-query",
    "TCBQ": "temporal-canvas-bitmap-query",
    "FDP": "filter-dataset-part",
    "NN": "nearest-neighbours"
}

CATYPES_TO_FEATURES = {
	"filter.image__feedbackModel.textQueryRelocation": ["TQR", "LK", "FDP"],
    "filter.image__feedbackModel.temporal.textQueryRelocation": ["TTQR", "LK", "FDP"],
	"filter.image__textQueryRelocation": ["TQR", "FDP"],
    "filter.image__temporal.textQueryRelocation": ["TTQR", "FDP"],
	"filter.image.text__feedbackModel.jointEmbedding": ["LK", "TQ", "FDP"],
    "filter.image.text__feedbackModel.jointEmbedding.temporal": ["LK", "TTQ", "FDP"],
	"filter.text__jointEmbedding": ["TQ"],
    "filter.text__jointEmbedding.temporal": ["TTQ"],
	"image__feedbackModel.localizedObjectBitmap": ["CBQ", "LK"],
    "image__feedbackModel.localizedObjectBitmap.temporal": ["TCBQ", "LK"],
    "image__feedbackModel.textQueryRelocation": ["TQR", "LK"],
    "image__feedbackModel.temporal.textQueryRelocation": ["TTQR", "LK"],
	"image__globalFeatures": ["NN"],
    "image__feedbackModel": ["LK"],
    "image__localizedObjectBitmap": ["CBQ"],
    "image__localizedObjectBitmap.temporal": ["TCBQ"],
	"image__textQueryRelocation": ["TQR"],
    "image__temporal.textQueryRelocation": ["TTQR"],
	"image.text__feedbackModel.jointEmbedding": ["LK", "TQ"],
    "image.text__feedbackModel.jointEmbedding.temporal": ["LK", "TTQ"],
	"image.text__feedbackModel.jointEmbedding.textQueryRelocation": ["LK", "TQR"],
    "image.text__feedbackModel.jointEmbedding.temporal.textQueryRelocation": ["LK", "TTQR"],
	"image.text__feedbackModel.localizedObjectText": ["CTQ", "LK"],
    "image.text__feedbackModel.localizedObjectText.temporal": ["TCTQ", "LK"],
	"image.text__jointEmbedding.textQueryRelocation": ["TQR"],
    "image.text__jointEmbedding.temporal.textQueryRelocation": ["TTQR"],
	"initial__initial": ["I"],
	"text__jointEmbedding": ["TQ"],
    "text__jointEmbedding.temporal": ["TTQ"],
	"text__jointEmbedding.localizedObjectText": ["TQ", "CTQ"],
    "text__jointEmbedding.localizedObjectText.temporal": ["TCTQ"],
	"text__localizedObjectText": ["CTQ"],
    "text__localizedObjectText.temporal": ["TCTQ"]
}

def names_features(x):
    return FEATURES[x]

def catypes_to_features(x):
    return CATYPES_TO_FEATURES[x]

def path(name):
    if (name in INSTANCES):
        return os.path.join(DATA_DIR, name)
    else:
        raise Exception("Uknown name!")

def name(instance_idx):
    return INSTANCES[instance_idx]

def dir_names():
    return DIR_NAMES

def out_dir(name, team=None):
    path = OUT_DIRS[name]
    if (team!=None):
        path = os.path.join(path, team)

    if not (os.path.exists(path)):
        os.makedirs(path, exist_ok=True)
        
    return path     

def thumbs_dir():
    return THUMBS_DIR     

def cache_dir(team = "", user=""):
    return os.path.join(CACHE_DIR, team, user)  

def cache_index_file():
    """
    Return filepath to the file where cached pieces are flaged.
    """
    return os.path.join(CACHE_DIR, "index.json")  

def thumbs_list_filepath():
    return THUMBS_LIST_DIR     

g_queries = set()

def queries():
    return g_queries

def push_query(q):
    g_queries.add(q)

