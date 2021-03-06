import numpy as np
import json
import os
import matplotlib.pyplot as plt
import seaborn as sb
import shutil
import pprint
pp = pprint.PrettyPrinter(indent=4)
# ---
import config
from constants import *
import utils

from raw_log_types import *
from results import *
from tasks import *
from task_results import *
from submits import *
from summary import *


class VbsVis:
    def __init__(self):


        # Load cached if available
        cached_file = os.path.join(config.cache_dir(), "vbs.pkl") 
        if (os.path.exists(cached_file)):
            print(f"Loading cached instance from {cached_file}...")
            cached_instance = utils.load_obj(cached_file)

            # pp.pprint(vars(cached_instance))
        
            self.verbose = cached_instance.verbose
            self._rewrite = cached_instance._rewrite
            self._tasks = cached_instance._tasks
            self._raw_summaries = cached_instance._raw_summaries
            self._summaries = cached_instance._summaries
            self._results = cached_instance._results
            self._task_results = cached_instance._task_results
            self._verdicts = cached_instance._verdicts

        # Else load everything
        else:
            self.verbose = False
            self._rewrite = False
            self._tasks = TaskDefs.parse_tasks(config.TASKS_JSON,
                                            config.TASKS_STARTS,
                                            config.TASK_MAPPING,
                                            config.thumbs_list_filepath(),
                                            verbose=self.verbose)

            self._verdicts = Verdicts(config.VERDICT_FILEPATH)

            self._raw_summaries = RawSummaries()
            self._summaries = Summaries(self._tasks)
            self._results = Results()
            self._task_results = TaskResults(self._tasks)

    # --- Getters/setters

    def raw_summaries(self) -> Summaries:
        return self._raw_summaries

    def summaries(self) -> Summaries:
        return self._summaries

    def task_submits(self) -> dict:
        return self._task_results._submits

    def task_results(self) -> TaskResults:
        return self._task_results

    def results(self) -> Results:
        return self._results

    def tasks(self) -> TaskDefs:
        return self._tasks
   
    def get_relevance_feedback_transitions(self, teams=None, users=None, tasks=None, 
        time=(0.0, 99999.0), timestamp=(0, 16242180131780), all=True, 
        file=None, file2=None, file_all=None, max=1154038
        ):

        # ANY-> liked
        any2liked = []
        # liked-> liked
        liked2liked = []

        for team, team_dict in self.summaries().summaries().items():
            if ((teams != None) and (not (team in teams))):
                continue
            
            for user, task_actions in team_dict.items():
                if ((users != None) and (not (user in users))):
                    continue
                    
                for task_name, actions in task_actions.items():
                    if ((tasks != None) and (not (task_name in tasks))):
                        continue
                    
                    task_results = self.task_results().task_results(team, user, task_name, time, timestamp)

                    prev = None
                    prev_changed = []
                    for r in task_results:
                        changed = r.c_changed()
                        pos_vid, pos_frame, _ = r.positions()

                        unpos_vid,unpos_frame, _ = prev.positions() if (prev != None) else (max, max, 0)
                        if (pos_vid == None):
                            continue
                        
                        if "LK" in changed and len(changed) == 1 and (not "NN" in prev_changed):
                            if (not "LK" in prev_changed):
                                trans = f"{prev_changed} -> {changed}"
                                
                                any2liked.append([r.timestamp(), user, pos_vid, pos_frame, unpos_vid, unpos_frame, trans])
                            else:
                                if all:                                    
                                    liked2liked.append([r.timestamp(), user, pos_vid, pos_frame, unpos_vid, unpos_frame, trans])

                        prev = r
                        prev_changed = changed

        if (file!= None):
            with open(file, "w", newline="") as ofs:
                writer = csv.writer(ofs, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["ID","user","pos_video","pos_frame","unpos_video","unpos_frame"])
                for x in any2liked:
                    writer.writerow(x)

        if (file2!= None):
            with open(file2, "w", newline="") as ofs:
                writer = csv.writer(ofs, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["ID","user","pos_video","pos_frame","unpos_video","unpos_frame"])
                for x in liked2liked:
                    writer.writerow(x)

        if (file_all!= None):
            with open(file_all, "w", newline="") as ofs:
                writer = csv.writer(ofs, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["ID","user","pos_video","pos_frame","unpos_video","unpos_frame"])
                for x in any2liked:
                    writer.writerow(x)

                for x in liked2liked:
                    writer.writerow(x)

        return any2liked + liked2liked

    # --- Printers

    def print_task_course(self, teams=None, users=None, tasks=None, time=(0.0, 99999.0), timestamp=(0, 16242180131780), events=["r", "s", "a"]):
        print("***############################***")
        print("***###*** TASK COURSES ***###***")
        print("***############################***")
        for team, team_dict in self.summaries().summaries().items():
            if ((teams != None) and (not (team in teams))):
                continue
            
            print(f"--- {team} ---")
            for user, task_actions in team_dict.items():
                if ((users != None) and (not (user in users))):
                    continue
                    
                print(f"\t--- {user} ---")
                for task_name, actions in task_actions.items():
                    if ((tasks != None) and (not (task_name in tasks))):
                        continue
                    
                    print(f"\t\t--- {task_name} ---\n")

                    actions = []
                    if ("a" in events):
                        actions = list(map(lambda x: (x.elapsed(), x), self.summaries().summary(team, user, task_name, time, timestamp)))
                    task_results = []
                    if ("r" in events):
                        task_results = list(map(lambda x: (x.elapsed(), x), self.task_results().task_results(team, user, task_name, time, timestamp)))
                    submits = []
                    if ("s" in events):
                        submits = list(map(lambda x: (x.elapsed(), x), self.task_results().task_submits(team, user, task_name, time, timestamp)))

                    all = sorted(actions + submits + task_results, key= lambda x: x[0])
                    
                    for x in all:
                        if isinstance(x, SummaryPoint):
                            print(x[1])
                        elif isinstance(x, ResultPoint):
                            print(x[1])
                        else:
                            print(x[1])

    def task_course(self, team, user, task_name, time=(0.0, 99999.0), timestamp=(0, 16242180131780), events=["r", "s", "a"]):
        
        actions = []
        if "a" in events:
            actions = list(map(lambda x: (x.elapsed(), x), self.summaries().summary(team, user, task_name, time, timestamp)))
        task_results = []
        if "r" in events:
            task_results = list(map(lambda x: (x.elapsed(), x), self.task_results().task_results(team, user, task_name, time, timestamp)))
        submits = []
        if "r" in events:
            submits = list(map(lambda x: (x.elapsed(), x), self.task_results().task_submits(team, user, task_name, time, timestamp)))

        all = sorted(actions + submits + task_results, key= lambda x: x[0])
        
        return all

    def task_actions_array(self, team, user, task_name, time=(0.0, 99999.0), timestamp=(0, 16242180131780)):
        
        times = []
        types = []
        actions = self.task_course(team, user, task_name, time, timestamp, events=["a"])
        
        for el, a in actions:
            times.append(a.elapsed())
            types.append(a.action())

        return times, types



    def print_tasks(self, tasks=None):
        self._tasks.print(tasks)

    def task_to_CSV(self, file):
        self._tasks.to_CSV(file)

    def print_results(self, team, user, fr, to):
        self.results().print_results(team, user, fr, to)

    def print_tool_features(self, teams=None):
        self.task_results().print_features(teams)

    def print_summary(self, teams=None, users=None, tasks=None, time=(0.0, 99999.0), timestamp=(0, 16242180131780)):
        self.summaries().print(teams, users, tasks, time, timestamp)

    def print_task_results(self, teams=None, users=None, tasks=None):
        self.task_results().print(teams, users, tasks)

    def print_task_results_arrays(self, teams=None, users=None, tasks=None):
        self.task_results().print_arrays(teams, users, tasks)

    def print_task_submits(self, teams=None, users=None, tasks=None):
        self.task_results().print_submits(teams, users, tasks)

    def print_task_submits_arrays(self, teams=None, users=None, tasks=None):
        self.task_results().print_submits_arrays(teams, users, tasks)

    def print_queries(self):
        for q in config.queries():
            print(q)

    # --- Statics

    @staticmethod
    def help():
        print("<<< ###################### >>>")
        print("<<< ###    VBS Viz     ### >>>")
        print("<<< ###################### >>>\n")

        print("INFO QUERIES:\n")

        print("vbs.print_tasks()")
        print("\t Prints the overview of the tasks that were presented.")


        print("PLOTS:\n")
        print("vbs.plot_timelines()")
        print("\t Plots timelines for all parsed teams/users/tasks.")
    
    @staticmethod
    def cache(instance):
        cached_file = os.path.join(config.cache_dir(), "vbs.pkl")    
        utils.save_obj(cached_file, instance)
        print(f"Instance cached to {cached_file}...")

    @staticmethod
    def flush_cache():
        cache_dir = config.cache_dir()
        try:
            shutil.rmtree(cache_dir)
        except:
            print('Error while deleting directory')

    # ---

    def parse_team(self,
                   team_name: str,
                   team_names: list,
                   verbose=False,
                   rewrite=False,
                   validate_fix=False,
                   generate_DRES=False,
                   validate_diff=False):

        self.verbose = verbose
        self._rewrite = rewrite

        print("==============\nTEAM: {}\n".format(team_name))

        if (team_name in self.task_results().task_results()):
            print("??? This team is already parsed. Cached maybe? ???")
            return

        ### main()
        if (validate_fix):
            self.validate_and_fix_input_data(team_name, team_names)

        if (validate_diff):
            self.calculate_server_ts_diff(team_name, team_names)

        if (generate_DRES):
            self.generate_DRES_logs(team_name, team_names)

        self.parse_logs(team_name, team_names)
        ###

        self.verbose = False
        self._rewrite = False

    def parse_logs(self, team_name: str, team_names: list):
        print("%%% PARSING %%%")

        for user_name in team_names:
            path = config.path(user_name)
            print("---\n+++ {} +++ \nDATA: {} \n".format(user_name, path))
            self.parse_user_submits(team_name, user_name, path)
            
        for user_name in team_names:
            print("---\n+++ {} +++ \nDATA: {} \n".format(user_name, path))
            path = config.path(user_name)
            self.parse_user_summary(team_name, user_name, path, self.task_submits())
            self.parse_user_results(team_name, user_name, path, self.task_submits(), self.summaries())


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

    def parse_user_submits(self, team, user_name, path):
        print("\t--- PARSING SUBMITS. ---")
        dir = config.dir_names()["requests"]
        full_path = os.path.join(path, dir)

        submits = []

        for filename in os.listdir(full_path):
            if not (filename.endswith("submit.json")):
                continue

            log = JsonLog.parse_file(full_path, filename)
            submits += log

        us = UserSubmits(submits)
        
        self._task_results.push_user_submits(team, user_name, us, self._verdicts)
        print("\t--- DONE. ---")

    def parse_user_results(self, team, user_name, path, submits, summaries : Summaries):
        print("\t--- PARSING TASK RESULTS. ---")
        dir = config.dir_names()["results"]
        full_path = os.path.join(path, dir)

        results = []

        for filename in os.listdir(full_path):
            log = JsonLog.parse_file(full_path, filename)
            results += log

        r = UserResults(results)
        #self._results.push_user_results(team, user_name, r)
        self._task_results.push_user_results(team, user_name, r, submits, summaries)
        print("\t--- DONE. ---")

    def parse_user_summary(self, team, user_name, path, submits):
        print("\t--- PARSING SUMMARY. ---")
        dir = config.dir_names()["summary"]
        full_path = os.path.join(path, dir)

        summary_logs = []

        for filename in os.listdir(full_path):
            log = SummaryLog.parse_file(full_path, filename)
            summary_logs += log.data()

        self.raw_summaries().push_user_summary(team, user_name, summary_logs)
        self.summaries().push_user_summary(team, user_name, summary_logs, submits)
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

            # Remove "rank" fields, they contain our internal frame ID
            for f in file_json["request"]["results"]:
                f.pop("rank")

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
