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




class SubmitPoint:
    def __init__(self, c, ts, elapsed):
        self._class = c

        self._ts = ts
        self._elapsed = elapsed

    def elapsed(self):
        return self._elapsed

    def timestamp(self):
        return self._ts

    def c(self):
        return self._class

    def __str__(self):
        s = f">>> {(self.elapsed() / 1000):.2f} <<<\n"
        s += f"- {self.c()} -\n"
        s += f"------------------------\n"
        return s

class SubmitPointsArrays:
    def __init__(self, submits):
        self._class = []
        self._ts = []
        self._elapsed = []

        for p in submits:
            self._class.append(p.c())
            self._ts.append(p.timestamp())
            self._elapsed.append(p.elapsed())


    def elapsed(self):
        return self._elapsed

    def timestamp(self):
        return self._timestamp

    def c(self):
        return self._class

    def __str__(self):
        s = "_elapsed:\n"
        s += self.elapsed().__str__() + "\n"

        s += "_class:\n"
        s += self.c().__str__() + "\n"

        return s

class ResultPointsArrays:
    def __init__(self, points):
        self._class = []

        self._ts = []
        self._elapsed = []
        self._pos_vid = []
        self._pos_fr = []
        self._num_reported = []

        self.submit_times = []
        self.submit_type = []

        for p in points:
            self._class.append(p.c())
            self._ts.append(p.timestamp())
            self._elapsed.append(p.elapsed())

            a, b, c = p.positions()

            self._pos_vid.append(a)
            self._pos_fr.append(b)
            self._num_reported.append(c)

    def elapsed(self):
        return self._elapsed

    def timestamp(self):
        return self._timestamp

    def c(self):
        return self._class

    def vid(self):
        return self._pos_vid

    def fr(self):
        return self._pos_fr

    def reported(self):
        return self._num_reported


    def __str__(self):
        s = "_elapsed:\n"
        s += self.elapsed().__str__() + "\n"

        s += "_class:\n"
        s += self.c().__str__() + "\n"

        s += "_video:\n"
        s += self.vid().__str__() + "\n"

        s += "_frame:\n"
        s += self.fr().__str__() + "\n"

        return s

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
        return self._ts

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
        self._task_results_arrays = {}
        self._submits = {}
        self._submits_arrays = {}

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

    def task_submits_arrays(self, team=None, user=None):
        if (user != None):
            return self._submits_arrays[team][user]
        elif (team != None):
            return self._submits_arrays[team]
        else:
            return self._submits_arrays

    
    def task_submits(self, team=None, user=None):
        if (user != None):
            return self._submits[team][user]
        elif (team != None):
            return self._submits[team]
        else:
            return self._submits

    def task_results_arrays(self, team=None, user=None):
        if (user != None):
            return self._task_results_arrays[team][user]
        elif (team != None):
            return self._task_results_arrays[team]
        else:
            return self._task_results_arrays

    
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

    def print_submits(self, teams=None, users=None, tasks=None):
        print("***############################***")
        print("***###***TASK SUBMITS ***###***")
        print("***############################***")

        for team, team_dict in self.task_submits().items():
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

    def print_submits_arrays(self, teams=None, users=None, tasks=None):
        print("***############################***")
        print("***###*** SUBMITS ARRAYS ***###***")
        print("***############################***")

        for team, team_dict in self.task_submits_arrays().items():
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

                    print(f"\t\t--- {task_name} ---")

                    print(points)

                    print(f"\t\t--------------------\n")
                    
        print("***############################***")


    def print_arrays(self, teams=None, users=None, tasks=None):
        print("***############################***")
        print("***###***  RESULT ARRAYS ***###***")
        print("***############################***")

        for team, team_dict in self.task_results_arrays().items():
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
                    
                    print(points)
                    print(f"\t\t--------------------\n")
                    
        print("***############################***")

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
            config.push_query(">>".join(qs))

            if (qs != None and len(qs) >=2):
                if (qs[0] != "") and (qs[1] != ""):
                    #print("TEMP")
                    r["usedTypes"].append("temporal")
        
    def push_user_submits(self, team, user, submits):

        if (not team in self._submits):
            self._submits[team] = {}
            self._submits_arrays[team] = {}
        
        self._submits[team][user] = {}
        self._submits_arrays[team][user] = {}
        
        i = 0
        for task in self._tasks.tasks():
            i+=1
            t_name = task.name()
            t_start, t_end = task.timestamps()
            t_target = task.target()
            
            full_t_name = t_name

            self._submits[team][user][full_t_name] = []
            self._submits_arrays[team][user][full_t_name] = []

            for r in submits.submits():
                ts = r["timestamp"]
                
                # Does it lie in this task?
                if (t_start > ts or ts > t_end):
                    continue
                
                elapsed = round((ts - t_start) / 1000, 2)

                c = None

                if (r["response"] == None):
                    c = "TIMEOUT"
                elif (r["response_code"] == 404):
                    c = "SERVER_LAG"
                elif ("submission" in r["response"]):
                        
                        if (r["response"]["submission"] == "CORRECT"):
                            c = "T"
                        elif (r["response"]["submission"] == "INDETERMINATE"):
                            c = "I"
                        else:
                            c = "F"

                s = SubmitPoint(c, ts, elapsed)

                self._submits[team][user][full_t_name].append(s)

            pts = SubmitPointsArrays(self._submits[team][user][full_t_name])
            self._submits_arrays[team][user][full_t_name] = pts

    def push_user_results(self, team, user, results):

        if (not team in self._task_results):
            self._task_results[team] = {}
            self._task_results_arrays[team] = {}
            self._classes[team] = set()
        
        self._task_results[team][user] = {}
        self._task_results_arrays[team][user] = {}
        
        i = 0
        for task in self._tasks.tasks():
            i+=1
            t_name = task.name()
            t_start, t_end = task.timestamps()
            t_target = task.target()
            
            full_t_name = t_name

            self._task_results[team][user][full_t_name] = []
            self._task_results_arrays[team][user][full_t_name] = []

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

                self._task_results[team][user][full_t_name].append(p)

            pts = ResultPointsArrays(self._task_results[team][user][full_t_name])
            self._task_results_arrays[team][user][full_t_name] = pts

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
