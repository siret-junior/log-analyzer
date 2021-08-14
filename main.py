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
        self.verbose = False
        self._tasks = TaskDefs.parse_tasks(config.TASKS_JSON,
                                           config.TASKS_STARTS,
                                           config.TASK_MAPPING,
                                           config.thumbs_list_filepath(),
                                           verbose=self.verbose)

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
   
    # --- Printers

    def print_tasks(self, tasks=None):
        self._tasks.print(tasks)

    def print_results(self, team, user, fr, to):
        self.results().print_results(team, user, fr, to)

    def print_tool_features(self, teams=None):
        self.task_results().print_features(teams)

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
                   validate_fix=False,
                   generate_DRES=False,
                   validate_diff=False):
        self.verbose = verbose

        print("==============\nTEAM: {}\n".format(team_name))

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

    def parse_logs(self, team_name: str, team_names: list):
        print("%%% PARSING %%%")
        cached_file = os.path.join(config.cache_dir(team_name), "results.pkl")
        cached_file2 = os.path.join(config.cache_dir(team_name),"task-results.pkl")
        
        cached_file4 = os.path.join(config.cache_dir(team_name),"classes.pkl")

        if (os.path.exists(cached_file)):
            print(">>>!!!<<< Using cached values. >>>!!!<<<")
            print(f"\t from: {cached_file}")

            x = utils.load_obj(cached_file)
            self._results._results[team_name] = x

            y = utils.load_obj(cached_file2)
            self._task_results.task_results()[team_name] = y

            z = utils.load_obj(cached_file3)
            self._task_results.queries()[team_name] = z

            zz = utils.load_obj(cached_file4)
            self._task_results.classes()[team_name] = zz
        else:
            for user_name in team_names:
                path = config.path(user_name)
                print("---\n\t +++ {} +++ \n\tDATA: {} \n".format(user_name, path))
                self.parse_user_submits(team_name, user_name, path)
                

            for user_name in team_names:
                path = config.path(user_name)
                print("---\n\t +++ {} +++ \n\tDATA: {} \n".format(user_name, path))
                self.parse_user_summary(team_name, user_name, path, self.task_submits())
                self.parse_user_results(team_name, user_name, path, self.task_submits(), self.summaries())

            utils.save_obj(cached_file, self._results.results(team_name))
            utils.save_obj(cached_file2, self._task_results.task_results(team_name))
            
            utils.save_obj(cached_file4, self._task_results.classes(team_name))

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
        print("\t\t--- PARSING SUBMITS. ---")
        dir = config.dir_names()["requests"]
        full_path = os.path.join(path, dir)

        submits = []

        for filename in os.listdir(full_path):
            if not (filename.endswith("submit.json")):
                continue

            log = JsonLog.parse_file(full_path, filename)
            submits += log

        us = UserSubmits(submits)
        
        self._task_results.push_user_submits(team, user_name, us)
        print("\t\t--- DONE. ---")

    def parse_user_results(self, team, user_name, path, submits, summaries : Summaries):
        print("\t\t--- PARSING TASK RESULTS. ---")
        dir = config.dir_names()["results"]
        full_path = os.path.join(path, dir)

        results = []

        for filename in os.listdir(full_path):
            log = JsonLog.parse_file(full_path, filename)
            results += log

        r = UserResults(results)
        self._results.push_user_results(team, user_name, r)
        self._task_results.push_user_results(team, user_name, r, submits, summaries)
        print("\t\t--- DONE. ---")

    def parse_user_summary(self, team, user_name, path, submits):
        print("\t\t--- PARSING SUMMARY. ---")
        dir = config.dir_names()["summary"]
        full_path = os.path.join(path, dir)

        summary_logs = []

        for filename in os.listdir(full_path):
            log = SummaryLog.parse_file(full_path, filename)
            summary_logs += log.data()

        self.raw_summaries().push_user_summary(team, user_name, summary_logs)
        self.summaries().push_user_summary(team, user_name, summary_logs, submits)
        print("\t\t--- DONE. ---")

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
