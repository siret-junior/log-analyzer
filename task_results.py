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


class ResultPoint:
    def __init__(self, c, ts, elapsed, value, pos_vid, pos_fr, num_reported):
        self._class = c

        self._ts = ts
        self._elapsed = elapsed
        self._value = value

        self._pos_vid = pos_vid
        self._pos_fr = pos_fr
        self._num_reported = num_reported

    def elapsed(self):
        return self._elapsed

    def timestamp(self):
        return self._timestamp

    def c(self):
        return self._class

    def value(self):
        return self._value

    def positions(self):
        return (self._pos_vid, self._pos_fr, self._num_reported)

    def __str__(self):
        s = f">>> {(self.elapsed() / 1000):.2f} <<<\n"
        s += f"- {self.c()} -\n"
        s += f"- {self.positions()} -\n"
        s += f"------------------------\n"
        #s += f"- {self.value()} -\n"
        return s


class TaskResults:
    def __init__(self, tasks):
        self._tasks = tasks
        self._task_results = {}
        self._classes = {}
        self._queries = {}

    # ---

    def queries(self, team=None, type=None):
        if (type != None):
            return self._queries[team][type]
        elif (team != None):
            return self._queries[team]
        else:
            return self._queries

    def classes(self, team=None):
        if (team != None):
            return self._classes[team]
        else:
            return self._classes

    def task_results(self, team=None, user=None):
        if (user != None):
            return self._task_results[team][user]
        elif (team != None):
            return self._task_results[team]
        else:
            return self._task_results

    # ---

    def __str__(self):
        s = "***############################***\n"
        s += "***###***TASK RESULT LOGS***###***\n"
        s += "***############################***\n"

    
        for team, team_dict in self.task_results().items():
            s += f"--- {team} ---\n"
            for user, user_results in team_dict.items():
                s += f"\t--- {user} ---\n"
                for task_name, points in user_results.items():
                    s += f"\t\t--- {task_name} ---\n\n"
                    #todo
                    s += f"\t\t Task has {len(points)} points.\n"
                    
                    s += f"\t\t--------------------\n\n"
                
        return s

    def print(self, teams=None, users=None, tasks=None):
        print("***############################***")
        print("***###***TASK RESULT LOGS***###***")
        print("***############################***")

        for team, team_dict in self.task_results().items():
            if ((teams != None) and (not (team in teams))):
                continue
            
            print(f"--- {team} ---")
            for user, user_results in team_dict.items():
                if ((users != None) and (not (user in users))):
                    continue
                    
                print(f"\t--- {user} ---")
                for task_name, points in user_results.items():
                    if ((tasks != None) and (not (task_name[3:] in tasks))):
                        continue
                    
                    print(f"\t\t--- {task_name} ---\n")
                    #todo
                    for p in points:
                        print(p)

                    print(f"\t\t--------------------\n")
                    
        print("***############################***")

    def print_features(self, teams):
        print("***#####################################***")
        print("***###*** TOOL FEATURES & STATES  ***###***")
        print("***#####################################***")

        for t, d in self._classes.items():
            if ((teams != None) and (not (t in teams))):
                continue

            print(f"--- {t} ---")
            for c in d:
                cc = config.catypes_to_features(c)
                ccc = ", ".join(sorted([config.names_features(x) for x in cc]))
                print(f"\t{cc} -> { ccc }")
    # ---

    def validate_and_fix_log(self, r):
        cats = r["usedCategories"]
        types = r["usedTypes"]
        val = r["values"][0]

        # Empty types | categories
        if (len(cats) == 0 or len(types) == 0):
            r["usedCategories"] = ["initial"]
            r["usedTypes"] = ["initial"]

        # Remove lifelog flags
        r["usedTypes"] = list(filter(lambda x: x != "lifelog", r["usedTypes"]))

        # Add "temporal" if temporal
        if ("text" in r["usedCategories"] and "jointEmbedding" in r["usedTypes"]):
            qs = utils.extract_text_query(val)
            #print(qs) 

            if (qs != None and len(qs) >=2):
                if (qs[0] != "") and (qs[1] != ""):
                    #print("TEMP")
                    r["usedTypes"].append("temporal")

        
    def push_user_results(self, team, user, results):

        if (not team in self._task_results):
            self._task_results[team] = {}
            self._classes[team] = set()
        
        self._task_results[team][user] = {}
        
        i = 0
        for task in self._tasks.tasks():
            i+=1
            t_name = task.name()
            t_start, t_end = task.timestamps()
            t_target = task.target()
            
            self._task_results[team][user][f"{i:02d}_{t_name}"] = []

            for r in results.results():
                ts = r["timestamp"]
                
                # Does it lie in this task?
                if (t_start > ts or ts > t_end):
                    continue
                
                # Fix some logs
                self.validate_and_fix_log(r)
                
                elapsed = ts - t_start
                cats = r["usedCategories"]
                types = r["usedTypes"]
                values = r["values"]
                frames = r["results"]
                
                catype = utils.generate_catype(cats, types)
                self._classes[team].add(catype)
                
                c = self.determine_result_class(cats, types, values)
                pos_vid, pos_fr, rep = self.determine_positions(frames, t_target)
                                
                p = ResultPoint(c, ts, elapsed, values, pos_vid, pos_fr, rep)
                
                self._task_results[team][user][f"{i:02d}_{t_name}"].append(p)

    def determine_positions(self, xs, target):

        if (target == None):
            return((None, None, len(xs)))

        t_video_ID = target.video_ID()
        t_from, t_to = target.interval()


        f_pos = 10000000
        v_pos = 10000000

        i = 0
        for x in xs:
            i+=1
            video_ID = int(x["item"])
            fnum = x["frame"]

            if (t_video_ID == video_ID):
                v_pos = min(i, v_pos)
                if (t_from <= fnum and fnum <= t_to):
                    f_pos = min(i, f_pos)
                    break



        return (v_pos, f_pos, len(xs))

    def determine_result_class(self, cats, types, value=None):
        features = config.catypes_to_features(
            utils.generate_catype(cats, types))
        return features
