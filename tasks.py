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

class TaskTarget:
    def __init__(self, video_ID, fnum_from, fnum_to):
        self._video_ID = video_ID
        self._fnum_from = fnum_from
        self._fnum_to = fnum_to

    def interval(self):
        return (self._fnum_from, self._fnum_to)

    def video_ID(self):
        return self._video_ID

    def __str__(self):
        s = "*** TaskTarget ***\n"
        s += f"\t\tvideo_ID: {self.video_ID()}\n"
        s += f"\t\tinterval: ({self.interval()[0]}, {self.interval()[1]})\n"

        return s


class Task:
    def __init__(self,
                 name,
                 type,
                 from_ts,
                 to_ts,
                 text=None,
                 target: TaskTarget = None):
        self._name = name

        # type \in { A, V, T }
        self._type = type
        self._from_ts = from_ts
        self._to_ts = to_ts

        self._text = text
        self._target = target

        if (self._type == "V" and self.text() != None):
            raise Exception("Visual tasks have no texts.")

        if (self._type == "A" and self.target() != None):
            raise Exception("AVS task cannot have target.")

    def name(self):
        return self._name

    def type(self):
        return self._type

    def timestamps(self):
        return (self._from_ts, self._to_ts)

    def times(self):
        tss = self.timestamps()
        return (utils.from_UNIX(tss[0]), utils.from_UNIX(tss[1]))

    def text(self):
        return self._text

    def target(self):
        return self._target

    def __str__(self):
        s = "\t*** Task ***\n"
        s += f"\tname: {self.name()}\n"
        s += f"\ttype: {self.type()}\n"
        s += f"\ttimestamps: ({self.timestamps()[0]}, {self.timestamps()[1]})\n"
        s += f"\ttimes: ({self.times()[0]}, {self.times()[1]})\n"
        s += f"\ttext: {self.text()}\n"
        s += f"\ttarget: {self.target().__str__()}\n"

        return s


class TaskDefs:
    def __init__(self, thumbs_list_filepath):
        self._tasks = []
        self.thumbs = {}

        with open(thumbs_list_filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:
                v_ID = int(row[0][0:5]) + 1  ## !!!
                fnum = int(row[0][42:50])

                if (not v_ID in self.thumbs):
                    self.thumbs[v_ID] = {}

                self.thumbs[v_ID][fnum] = row[0]

        #pp.pprint(self.thumbs)

    def tasks(self):
        return self._tasks

    def task(self, idx: int):
        return self._tasks[idx]

    def task(self, name: str):
        for t in self._tasks:
            if (t.name() == name):
                return t

    def print(self):
        print("***############################***")
        print("***###*** VBS 2021 TASKS ***###***")
        print("***############################***")

        print(">>>>>>>>>>>>> STATS <<<<<<<<<<<<<<<<")

        print("Number of tasks: {}".format(len(self._tasks)))

        # Print unique video IDs
        unique_v_IDs = set()
        for t in self._tasks:
            if (t.target() != None):
                unique_v_IDs.add(t.target().video_ID())

        print("Unique video IDs: ")
        for u in sorted(unique_v_IDs):
            print(u, end=", ")
        print("")

        print(">>>>>>>>>>>>> TASKS <<<<<<<<<<<<<<<<")
        for t in self._tasks:
            print(t.__str__() + "")

            if (t.target() != None):
                v_ID = t.target().video_ID()
                fr, to = t.target().interval()

                fnms = self.filenames(v_ID, fr, to)
                fnms = list(
                    map(lambda x: os.path.join(config.thumbs_dir(), x), fnms))

                utils.print_images_row(fnms)

            print("------------------------------------")

    def filename(v_ID, fnum):
        return self.thumbs[v_ID][fnum]

    def filenames(self, v_ID, fr, to, limit=5):
        fnums = self.thumbs[v_ID].keys()

        res = []
        for n in fnums:
            if (fr <= n and n <= to):
                res.append(self.thumbs[v_ID][n])

        return res

    @staticmethod
    def parse_tasks(tasks_fpth,
                    tasks_ends_fpth,
                    mapping_fpth,
                    thumbs_list_fpth,
                    verbose=False):
        print("%%% PARSING TASKS %%%")

        tasks_JSON = None
        with open(tasks_fpth) as ifs:
            tasks_JSON = json.load(ifs)["tasks"]

        guid_to_video_ID = {}
        guid_to_FPS = {}
        with open(mapping_fpth) as ifs_mapping:
            mapping_reader = csv.reader(ifs_mapping, delimiter=',')
            for row in mapping_reader:
                if (len(row) < 3):
                    break
                guid_to_video_ID[row[0]] = int(row[1])
                guid_to_FPS[row[0]] = float(row[2])

        tdefs = TaskDefs(thumbs_list_fpth)

        count = 0
        with open(tasks_ends_fpth) as ifs_starts:
            starts_reader = csv.reader(ifs_starts, delimiter=',')

            for row in starts_reader:
                count += 1
                t_name = row[2]

                if (verbose):
                    print("\t ...Task {} parsed.".format(t_name))

                t = utils.find_task_def(tasks_JSON, t_name)
                t_datetime = "{}T{}".format(row[0], row[1])

                t_type = t["taskType"][0:1]
                t_tsfrom = utils.UNIX_from_datetime(t_datetime)
                t_tsto = t_tsfrom + (t["duration"] * 1000)  #ms

                text = None
                if (t_type == "T"):
                    text = ""
                    for c in t["components"]:
                        text = c["description"]

                elif (t_type == "A"):
                    text = t["components"][0]["description"]

                t_target = None
                if (t_type != "A"):
                    guid = t["target"]["mediaItems"][0]["mediaItem"]

                    fps = guid_to_FPS[guid]
                    vid_ID = guid_to_video_ID[guid]

                    fr = t["target"]["mediaItems"][0]["temporalRange"][
                        "start"]["value"] * fps
                    to = t["target"]["mediaItems"][0]["temporalRange"]["end"][
                        "value"] * fps

                    if (t["target"]["mediaItems"][0]["temporalRange"]["start"]
                        ["unit"] != "SECONDS"):
                        raise Exception("Invalid value type.")

                    t_target = TaskTarget(vid_ID, fr, to)

                task = Task(t_name, t_type, t_tsfrom, t_tsto, text, t_target)
                tdefs._tasks.append(task)

        print(f"%%% Parsed {count} tasks. %%%")
        print("%%% DONE! %%%")
        return tdefs

    def __str__(self):
        s = "*** TaskDefs ***\n"

        for t in self._tasks:
            s += t.__str__() + "\n"

        return s

