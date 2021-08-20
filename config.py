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

TIME_TO_CORRECT_SUBMIT_FILEPATH = os.path.join(DATA_DIR, "stats/time-until-submit.csv")

def time_to_corr_submit_file():
    return TIME_TO_CORRECT_SUBMIT_FILEPATH

VERDICT_FILEPATH = os.path.join(DATA_DIR, "judgments.njson")

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

def classes_to_flags(xs):

    is_initial = False
    is_text = False
    is_bitmap = False
    is_nn = False

    is_reloc = False
    is_canvas = False
    is_filter = False

    is_temporal = False
    is_like = False

    if "I" in xs:
        is_initial = True
    if "TQ" in xs:
        is_text = True
    if "TTQ" in xs:
        is_text = True
        is_temporal = True
    if "LK" in xs:
        is_like = True

    if "TQR" in xs:
        is_text = True
        is_reloc = True
    if "TTQR" in xs:
        is_text = True
        is_temporal = True
        is_reloc = True
    if "CTQ" in xs:
        is_canvas = True
        is_text = True
    if "TCTQ" in xs:
        is_canvas = True
        is_text = True
        is_temporal = True
    if "CBQ" in xs:
        is_bitmap = True
        is_canvas = True
    if "TCBQ" in xs:
        is_bitmap = True
        is_canvas = True
        is_temporal = True
    if "FDP" in xs:
        is_filter = True
    if "NN" in xs:
        is_nn = True

    return is_initial, is_nn, is_text, is_bitmap, is_like, is_temporal, is_reloc, is_canvas, is_filter


def classes_to_changed_flags(xs):

    is_initial = False
    is_text = False
    is_bitmap = False
    is_nn = False

    is_reloc = False
    is_canvas = False
    is_filter = False

    is_temporal = False
    is_like = False

    if "I" in xs:
        is_initial = True
    if "TQ" in xs:
        is_text = True
    if "TTQ" in xs:
        is_text = True
        is_temporal = True
    if "LK" in xs:
        is_like = True

    if "TQR" in xs:
        is_text = True
        is_reloc = True
    if "TTQR" in xs:
        is_text = True
        is_temporal = True
        is_reloc = True
    if "CTQ" in xs:
        is_canvas = True
        is_text = True
    if "TCTQ" in xs:
        is_canvas = True
        is_text = True
        is_temporal = True
    if "CBQ" in xs:
        is_bitmap = True
        is_canvas = True
    if "TCBQ" in xs:
        is_bitmap = True
        is_canvas = True
        is_temporal = True
    if "FDP" in xs:
        is_filter = True
    if "NN" in xs:
        is_nn = True

    return is_initial, is_nn, is_text, is_bitmap, is_like, is_temporal, is_reloc, is_canvas, is_filter

def action_type_to_y(type):
    return 0

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


#
# Used node IDs
#
# {   'CollageHunter': {   'collage-jakub': {   'node01ngnncxfsgl60j99fpvtp9m3921167',
#                                               'node0aia2lfypnc4f17hau0w5fg1l64538',
#                                               'node0uc2wf1nbxqmo1hppwyzogdfgp39278'},
#                          'collage-premek': {   'node01f9021gqrae2cw9d5ayp5i3s20897',
#                                                'node0aqq18ironvoy1rtiap6cifyoc4539',
#                                                'node0jhwgl6vwprow17ps71dv28nj739279'}},
#     'LegacySOMHunter': {   'legacy-franta-tomas': {   'node01v08kpdn5ejco1mh586d2518vx2750',
#                                                       'node07ip07glwt7qkhmqxanw92fh420354',
#                                                       'node0t9pskdf6upx91e7ynaxszo97b44577'},
#                            'legacy-tereza': {   'node022qhvmzkyj431jajifyc4evyk34287',
#                                                 'node09semc6ulbf9yfr3bp9tayiwl2778',
#                                                 'node0q99omz6ljdpt9l6qfj3s0z5x21912',
#                                                 'node0yul2upqjr1lhl3o14gppbf7z31293'}},
#     'SOMHunter': {   'sh-patrik': {   'node01102699zyqjkpe493h9qqe29y42675',
#                                       'node016tr3yaku2hvb16miqz8qo33b72754',
#                                       'node017wz3mxftf5ujf9jyldut60q645340',
#                                       'node01mchg4acd0fxd141b9168hibto4559',
#                                       'node01pjk2d5bepwislvql97fws6x439280',
#                                       'node01rtkj4ep7y46c3m2l7iuxu6yk21687',
#                                       'node01wvqu10mjrry6wuufa8pexsqj4403',
#                                       'node01xvq1w5xm3cpl1ob2obbdv60ug51194',
#                                       'node036wxkatjx4u66jacjr7unf6k40056',
#                                       'node07loazqplpn11sikywgx1dfxz33582',
#                                       'node0tnyeex3cimqsm36p0n9maaks45373'},
#                      'sh-vit': {   'node01hrt4nwhwvsy91sq9yy8nfr86i42054',
#                                    'node01ibysb1bsmyed1vmhbv9fnqh652760',
#                                    'node01xawp9sngqnyj2vgejub0kny822032'}}}

# TNAME2PAPER_NAME = {
#     "01"
# }

ALL_TEAMS2HASH = {
    "vitrivr": "f3bc2977-0e56-4984-a46e-08ebad673bdb",
    "VIRET": "f43dc2f2-0e0b-40d8-bfb0-f019bc895b5b",
    "Vireo": "b11e55a0-caed-4001-9e03-11b05b38288b",
    "SOMHunter": "c69fbcda-041c-458f-b4e7-5e2e3c1f9489",
    "HTW": "04938928-4ae8-4dcf-bc96-8b3b758c521c",
    "CollageHunter": "b231f852-86ea-4f7f-84bd-b2f87a94e467",
    "VERGE": "4449ae20-04f9-44dc-aed2-cec6330c3e83",
    "LegacySOMHunter": "0a2860d2-b2c9-4fe5-adc2-c02534b25911",
    "vitrivr-vr": "443d8be7-e381-4fbd-ba46-ff2514db3117",
    "Exquisitor": "03506772-94b4-4409-9e7e-f4716fe7ee79",
    "VISIONE": "7bf90d4b-a2e6-49db-b7af-b7dbb91d01e7",
    "diveXplore": "49eed368-181d-407c-8cbc-ef54b8d495f9",
    "VideoGraph": "a265bf53-7e8c-4122-92bc-ee38772d1058",
    "noshot": "a2856f06-299f-46f3-aed4-b142f7d067da",
    "IVIST": "15525fab-f7b9-4106-ac00-05407d5b04af",
    "IVOS": "8488d7cb-736a-4c7b-8113-a892b09e15cc",
    "EOLAS": "a88dc70e-d120-4262-b8a0-7f579f372b7c"
}

def avs_pos():
    return 10

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

def all_teams(): 
    return ALL_TEAMS2HASH
