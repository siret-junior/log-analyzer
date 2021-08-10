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


#
# Summary log type
#
class SummaryLog:
    """
    Represents one summary log file.
    """
    def __init__(self):
        self.data = []

    @staticmethod
    def parse_file(full_path, filename):

        log = SummaryLog()
        fpth = os.path.join(full_path, filename)

        with open(fpth, 'r') as ifs:
            line = ifs.readline()
            while (line):
                log.parse_line(line)
                line = ifs.readline()

        return log

    def parse_line(self, line):
        self.data.append(line)


#
# JSON log type
#
class JsonLog:
    """
    Represents one JSON log file.
    """
    def __init__(self):
        pass

    @staticmethod
    def fix_JSON(JSON_text, filename):

        if (len(JSON_text) == 0):
            raise Exception("File {} is empty!".format(filename))

        #
        # Remove an extra comma at the end of the file
        #
        comma_idx = JSON_text.rfind(",")
        text_len = len(JSON_text)
        if (comma_idx >= text_len - 3):
            JSON_text = JSON_text[0:comma_idx] + "\n"

        #
        # Wrap submit logs with an array, cause there may be multiple submits at the same millisecond
        #
        if (filename.endswith("submit.json")):
            JSON_text = "[{}]".format(JSON_text)

        fixed = JSON_text

        try:
            parsed = json.loads(fixed)
            return fixed
        except:
            print(fixed)
            raise Exception("nende")

    @staticmethod
    def parse_file(full_path, filename):
        fpth = os.path.join(full_path, filename)
        parsed = None
        with open(fpth, 'r') as ifs:
            try:

                parsed = json.load(ifs)
                if (filename.endswith("submit.json") and type(parsed) is dict):
                    raise Exception("!!")
            except:
                ifs.seek(0)
                text = ifs.read()

                parsed = JsonLog.fix_JSON(text, filename)
                ifs.close()

                stinfo = os.stat(fpth)
                with open(fpth, 'w') as ofs:
                    ofs.write(parsed)
                    print("W: Rewritten the file {}!".format(filename))
                os.utime(fpth, (stinfo.st_atime, stinfo.st_mtime))
        return parsed


class UserResults:
    def __init__(self, results_list):
        self._results = results_list

    def size(self):
        return len(self._results)

class Results:
    def __init__(self):
        self._results = {}
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)
        
        
    def push_user_results(self, team, user, results):
        if (not team in self._results):
            self._results[team] = {}

        self._results[team][user] = results
        
    def results(self, team=None, user = None):
        if (user != None):
            return self._results[team][user]
        elif (team != None):
            return self._results[team]
        else:
            return self._results
    
    def __str__(self):
        s = "***############################***\n"
        s += "***###***   RESULT LOGS  ***###***\n"
        s += "***############################***\n"
        
    
        for team, team_dict in self.results().items():
            s += f"--- {team} ---\n"
            for user, user_results in team_dict.items():
                s += f"\t--- {user} ---\n\n"
                
                s += f"\tUser has {user_results.size()} result logs.\n"
                
                s += f"\t--------------------\n\n"
                
        return s
        


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


class Data:
    def __init__(self):
        self.verbose = False

        self._tasks = TaskDefs.parse_tasks(config.TASKS_JSON,
                                          config.TASKS_STARTS,
                                          config.TASK_MAPPING,
                                          config.thumbs_list_filepath(),
                                          verbose=self.verbose)


        self._results = Results()

    def parse_team(self,
                   team_name: str,
                   team_names: list,
                   verbose=False,
                   validate_fix=False,
                   generate_DRES=False):
        self.verbose = verbose

        print("==============\nTEAM: {}\n".format(team_name))

        ### main()
        if (validate_fix):
            self.validate_and_fix_input_data(team_name, team_names)

        self.calculate_server_ts_diff(team_name, team_names)

        if (generate_DRES):
            self.generate_DRES_logs(team_name, team_names)

        self.parse_results(team_name, team_names)
        ###

        self.verbose = False

    def parse_results(self, team_name: str, team_names: list):
        print("%%% PARSING RESULTS %%%")
        cached_file = os.path.join(config.cache_dir(team_name), "results.pkl")

        if (os.path.exists(cached_file)):
            print(">>>!!!<<< Using cached values. >>>!!!<<<")
            print(f"\t from: {cached_file}")

            x = utils.load_obj(cached_file)
            self._results._results[team_name] = x
        else:
            
            for user_name in team_names:
                path = config.path(user_name)

                print("---\n\t +++ {} +++ \n\tDATA: {} \n".format(user_name, path))
                self.parse_user_results(team_name, user_name, path)
            
            utils.save_obj(cached_file, self._results.results(team_name))

        print("%%% DONE! %%%")

    def validate_and_fix_input_data(self, team_name: str, team_names: list):
        print("%%% VALIDATING & FIXING %%%")

        for user_name in team_names:
            path = config.path(user_name)

            print("---\n\t +++ {} +++ \n\tDATA: {} \n".format(user_name, path))

            self.parsed[team_name] = self.validate_user(user_name, path)

        print("%%% DONE! %%%")

    def calculate_server_ts_diff(self, team_name: str, team_names: list):
        print("%%% CALCULATING SERVER TS DIFF %%%")

        diffs = []
        for user_name in team_names:
            path = config.path(user_name)

            print("---\n\t +++ {} +++ \n\tDATA: {} \n".format(user_name, path))

            ds = self.calculate_server_ts_diff_for_user(user_name, path)

            diffs.append(ds)

        #pp.pprint(diffs)

        mins = []

        for dfs in diffs:
            mins.append(np.min(np.array(dfs)))

        i = 0
        for user_name in team_names:
            print("DIFF MIN FOR {}: {}".format(user_name, mins[i]))
            i += 1

        print("%%% DONE! %%%")

        return mins

    def parse_user_results(self, team, user_name, path):
        dir = config.dir_names()["results"]
        full_path = os.path.join(path, dir)

        results = []

        for filename in os.listdir(full_path):

            log = JsonLog.parse_file(full_path, filename)
            results += log

        r = UserResults(results)
        self._results.push_user_results(team, user_name, r)

        print("\t--- DONE. ---")

    def generate_DRES_logs(self, team_name: str, team_names: list):
        print("%%% GENERATING DRES LOG FILES %%%")

        for user_name in team_names:
            path = config.path(user_name)

            print("---\n\t +++ {} +++ \n\tDATA: {} \n".format(user_name, path))

            self.generate_DRES_results_for_user(team_name, user_name, path)

        print("%%% DONE! %%%")

    def calculate_server_ts_diff_for_user(self, user_name, path):
        dir = config.dir_names()["actions"]

        diffs = []

        if (self.verbose):
            print("\t--- DIR: {} ---".format(dir))

        full_path = os.path.join(path, dir)

        for filename in os.listdir(full_path):
            actions = JsonLog.parse_file(full_path, filename)

            for a in actions:
                ser_ts = a["metadata"]["serverTimestamp"]
                loc_ts = a["metadata"]["timestamp"]
                diff = ser_ts - loc_ts

                if ser_ts < 10000:
                    continue

                diffs.append(diff)

        if (self.verbose):
            print("\t--- DONE. ---")

        return diffs

    def generate_DRES_results_for_user(self, team_name, user_name, path):
        dir = config.dir_names()["requests"]
        out_dir = config.out_dir("dres")

        if (self.verbose):
            print("\t--- DIR: {} ---".format(dir))
            print("\t--- OUT: {} ---".format(out_dir))

        full_path = os.path.join(path, dir)

        # For each file in the 'requests' directory
        for filename in os.listdir(full_path):
            if (not filename.endswith("result.json")):
                continue

            file_json = JsonLog.parse_file(full_path, filename)
            stinfo = os.stat(os.path.join(full_path, filename))

            ts = file_json["timestamp"]
            file_json["request"]["timestamp"] = ts

            user_out_dir = os.path.join(out_dir, team_name, user_name)
            os.makedirs(user_out_dir, exist_ok=True)

            fpth = os.path.join(user_out_dir, "{}.json".format(ts))

            with open(fpth, "w") as ofs:
                ofs.write(json.dumps(file_json["request"], indent=4))

            os.utime(fpth, (stinfo.st_atime, stinfo.st_mtime))

        if (self.verbose):
            print("\t--- DONE. ---")

    def validate_user(self, user_name, path):
        for _, dir in config.dir_names().items():

            if (self.verbose):
                print("\t--- DIR: {} ---".format(dir))

            full_path = os.path.join(path, dir)
            for filename in os.listdir(full_path):

                if (filename.endswith("log")):
                    SummaryLog.parse_file(full_path, filename)
                else:
                    JsonLog.parse_file(full_path, filename)

            if (self.verbose):
                print("\t--- DONE. ---")

    def results(self):
        return self._results

    def print_tasks(self):
        self._tasks.print()

    @staticmethod
    def flush_cache():
        cache_dir = config.cache_dir()
        print(cache_dir)
        try:
            shutil.rmtree(cache_dir)
        except:
            print('Error while deleting directory')