from summary import Summaries
from tasks import TaskDefs
import numpy as np
import csv
import json
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sb
import shutil
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)

import config
import utils

from results import *
from submits import *


class SubmitPoint:
    def __init__(self, c, ts, elapsed, node):
        self._class = c

        self._ts = ts
        self._elapsed = elapsed
        self._node = node

    def node(self):
        return self._node

    def elapsed(self):
        return self._elapsed

    def timestamp(self):
        return self._ts

    def c(self):
        return self._class

    def __str__(self):
        s = f"--->>> {self.elapsed()} --->>>\n"
        s += f"- SUBMIT REQUEST-\n"
        s += f"- {self.c()} -\n"
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
        self._class_changed = []

        self._ts = []
        self._elapsed = []
        self._pos_vid = []
        self._pos_fr = []
        self._num_reported = []
        self._values = []

        self.submit_times = []
        self.submit_type = []

        for p in points:
            self._class.append(p.c())
            self._class_changed.append(p.c_changed())
            self._ts.append(p.timestamp())
            self._elapsed.append(p.elapsed())

            a, b, c = p.positions()
            self._values.append(p.value())
            self._pos_vid.append(a)
            self._pos_fr.append(b)
            self._num_reported.append(c)

    def values(self):
        return self._values

    def elapsed(self):
        return self._elapsed

    def timestamp(self):
        return self._ts

    def c(self):
        return self._class

    def c_changed(self):
        return self._class_changed

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
        self._changed = []

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

    def c_changed(self):
        return self._changed

    def value(self):
        return self._value

    def positions(self):
        return (self._pos_vid, self._pos_fr, self._num_reported)

    def __str__(self):
        s = f"\t\t###!!!### {self.elapsed():.2f} ###!!!###\n"
        s += f"\t\t- REPORT RESULTS -\n"
        s += f"\t\t- {self.c()} -\n"
        s += f"\t\t- {self.c_changed()} -\n"
        s += f"\t\t- {self.positions()} -\n"
        s += f"\t\t- {self.value()} -\n"
        return s


class TaskResults:
    def __init__(self, tasks : TaskDefs):
        self._tasks = tasks
        
        self._task_results = {}
        self._task_results_arrays = {}
        self._submits = {}
        self._submits_arrays = {}

        self._classes = {}
        self._classes_changed = {}
        self._queries = {}

        
        self._nodes = {}


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

    
    def task_submits(self, team=None, user=None, task=None, time=(0.0, 99999.0), timestamp=(0, 16242180131780)):
        if (task != None):
            res = []

            for a in self._submits[team][user][task]:
                a_el = a.elapsed()
                a_ts = a.timestamp()
                if  (timestamp[0] <= a_ts and a_ts <= timestamp[1]) and (time[0] <= a_el and a_el <= time[1]):
                    res.append(a)
            return res
        elif (user != None):
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

    
    def task_results(self, team=None, user=None, task=None, time=(0.0, 99999.0), timestamp=(0, 16242180131780)):
        if (task != None):
            res = []

            for a in self._task_results[team][user][task]:
                a_el = a.elapsed()
                a_ts = a.timestamp()
                if  (timestamp[0] <= a_ts and a_ts <= timestamp[1]) and (time[0] <= a_el and a_el <= time[1]):
                    res.append(a)
            return res
        elif (user != None):
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
                    if ((tasks != None) and (not (task_name in tasks))):
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
                    if ((tasks != None) and (not (task_name in tasks))):
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
                    if ((tasks != None) and (not (task_name in tasks))):
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
                    if ((tasks != None) and (not (task_name in tasks))):
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
        
    def push_user_submits(self, team, user, submits, verdicts : Verdicts):

        if (not team in self._submits):
            self._submits[team] = {}
            self._submits_arrays[team] = {}
            self._nodes[team] = {}
    
        self._nodes[team][user] = set()
        self._submits[team][user] = {}
        self._submits_arrays[team][user] = {}
        
        i = 0
        for task in self._tasks.tasks():
            i+=1
            t_dur = task.duration()
            t_type = task.type()
            t_name = task.name()
            t_start, t_end = task.timestamps()
            t_target = task.target()
            
            full_t_name = t_name

            self._submits[team][user][full_t_name] = []
            self._submits_arrays[team][user][full_t_name] = []

            for r in submits.submits():
                ts = r["timestamp"]
                elapsed = round((ts - t_start) / 1000, 2)

                # Does it lie in this task?
                if (t_start > ts or ts > t_end):
                    continue
            

                c, node = utils.determine_submit_result(r, verdicts)
                self._nodes[team][user].add(node)

                if (c == None):
                    pp.pprint(r)

                s = SubmitPoint(c, ts, elapsed, node)

                self._submits[team][user][full_t_name].append(s)

            pts = SubmitPointsArrays(self._submits[team][user][full_t_name])
            self._submits_arrays[team][user][full_t_name] = pts

    def push_user_results(self, 
        team : str, user : str, 
        results : UserResults, submits : dict, summaries : Summaries):

        if (not team in self._task_results):
            self._task_results[team] = {}
            self._task_results_arrays[team] = {}
            self._classes[team] = set()
            self._classes_changed[team] = set()
        
        self._task_results[team][user] = {}
        self._task_results_arrays[team][user] = {}
        
        i = 0
        for task in self._tasks.tasks():
            i+=1
            t_name = task.name()
            t_type = task.type()
            t_start, t_end = task.timestamps()
            t_target = task.target()
            t_dur = task.duration()

            full_t_name = t_name

            self._task_results[team][user][full_t_name] = []
            self._task_results_arrays[team][user][full_t_name] = []

            eartliest_submit_time = t_dur
            
            if t_type != "A":
                for _, u_submits in submits[team].items():
                    for s in u_submits[t_name]:
                        if (s.c() == "T"):
                            elapsed = s.elapsed()

                            eartliest_submit_time = min(eartliest_submit_time, elapsed)

            prev = None
            for r in results.results():
                ts = r["timestamp"]
                
                # Does it lie in this task?
                if (t_start > ts or ts > t_end):
                    continue

                # Fix some logs
                self.validate_and_fix_log(r)
                
                elapsed = round((ts - t_start) / 1000, 2)

                #
                # Cut logs after the submit
                #
                if (elapsed > eartliest_submit_time):
                    break

                cats = r["usedCategories"]
                types = r["usedTypes"]
                values = r["values"]
                frames = r["results"]
                
                catype = utils.generate_catype(cats, types)
                self._classes[team].add(catype)
                
                c = self.determine_result_class(cats, types, values)
                pos_vid, pos_fr, rep = self.determine_positions(frames, t_target)
                                
                p = ResultPoint(c, ts, elapsed, values, pos_vid, pos_fr, rep)
                prev = p
                self._task_results[team][user][full_t_name].append(p)

            if prev != None:
                prev = copy.deepcopy(prev)
                prev._elapsed = eartliest_submit_time
                self._task_results[team][user][full_t_name].append(prev)

            team_user_task_result_points = self._task_results[team][user][full_t_name]
            team_user_task_sumarries = summaries.summary(team, user, full_t_name)

            self.detect_changed_features(team_user_task_result_points, team_user_task_sumarries)

            pts = ResultPointsArrays(team_user_task_result_points)
            self._task_results_arrays[team][user][full_t_name] = pts

    def determine_positions(self, xs, target):

        if (target == None):
            return((None, None, len(xs)))

        t_video_ID = target.video_ID()
        t_from, t_to = target.interval()


        f_pos = config.max_pos()
        v_pos = config.max_pos()

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

    def detect_changed_features(self, result_points : list, summary) -> list:
        changeds = []
        i_s = 0

        prev = None
        prev_time = 0
        for ii, p in enumerate(result_points):
            if (ii >= len(result_points) - 1):
                break

            changed = []
            fr = prev_time
            to = p.elapsed()

            while summary[i_s].elapsed() <= fr:
                
                #print(f"{summary[i_s].elapsed()} <= {fr}")
                i_s +=1

            like = False
            text_change = True

            all = False

            int_actions = []
            while i_s < len(summary) and summary[i_s].elapsed() < to:
                #print(f"{summary[i_s].elapsed()} < {to}")
                s = summary[i_s]
                int_actions.append((s.elapsed(), s.action()))
                i_s +=1

                if (s.action() == "resetAll"):
                    all = True
                if (s.action() == "like"):
                    like = True
                if (s.action() == "textQueryChange"):
                    text_change = True

            prev_cs = prev.c() if prev !=None else []
            curr_cs = p.c()

            if all or (len(curr_cs) == 1):
                changed = curr_cs
      
            elif prev !=None: 
       
                if (prev.c() == p.c()):
              

                    if "NN" in curr_cs:
                        changed.append("NN")
                    if (like):
                        changed.append("LK")

                    if (text_change and (p.value() != prev.value() or p.positions() == prev.positions())):
                   
                        if "TQ" in curr_cs:
                            changed.append("TQ.")
                        if "TTQ" in curr_cs:
                            changed.append("TTQ")

                    # Exclusion method
                    if (len(changed) == 0):
                        

                        cc = copy.copy(curr_cs)
                        if "LK" in cc:
                            cc.remove("LK")
                        if "FDP" in cc:
                            cc.remove("FDP")
                        if "TQ" in cc:
                            cc.remove("TQ")
                        if "TTQ" in cc:
                            cc.remove("TTQ")

                        if (len(cc) == 1):
                            changed=cc
                        else:
                            print(">>>>>>")
                            print(prev)
                            print(p)
                            print(">>>>>>")
                            raise Exception("Cannot unambiguously determine the change!")
                            #pp.pprint(cc)
                else:
                    
                    for c in curr_cs:
                        if not (c in prev_cs):
                            changed.append(c)

            else:
                changed = p.c()

            #
            # Debug print
            #
            # if (len(changed) == 0):
            #     print("~~~~~~~")
            #     #pp.pprint(int_actions)
            #     print(prev.c() if prev != None else "-")
            #     print(p.c())
            #     print("=>>")
            #     print(changed)

            p._changed = changed
            prev = p
            prev_time = p.elapsed()
