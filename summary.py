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


class RawSummaries:
    def __init__(self):
        self._data = {}


    def push_user_summary(self, team, user, summary : list):

        if (not team in self._data):
            self._data[team] = {}
        
        self._data[team][user] = summary




class SummaryPoint:
    def __init__(self, action ,ts, elapsed, time, values):
        self._action = action
        self._ts = ts
        self._elapsed = elapsed
        self._time = time
        self._values = values

    def action(self):
        return self._action

    def time(self):
        return self._time

    def elapsed(self):
        return self._elapsed

    def timestamp(self):
        return self._ts

    def values(self):
        return self._values

    def __str__(self):
        s += f"\t--- {self.elapsed()} ---\n"
        s += f"\action: {self.action()}\n"
        s += f"\ttime: {self.time()}\n"
        s += f"\ttimestamp: {self.timestamp()}\n"

        return s

class Summaries:
    def __init__(self, tasks):
        self._tasks = tasks
        self._data = {}

    def summary(self, team, user, task):
        return self._data[team][user][task]

    def print(self, teams=None, users=None):
        print("***############################***")
        print("***###*** ACTION SUMMARIES ***###***")
        print("***############################***")

        for team, team_dict in self.task_submits().items():
            if ((teams != None) and (not (team in teams))):
                continue
            
            print(f"--- {team} ---")
            for user, actions in team_dict.items():
                if ((users != None) and (not (user in users))):
                    continue
                    
                print(f"\t--- {user} ---")

                for a in actions:
                    print(a)

                print(f"\t\t--------------------\n")

    def push_user_summary(self, team, user, summaries : list, submits):

        if (not team in self._data):
            self._data[team] = {}
        
        self._data[team][user] = {}
        
        for task in self._tasks.tasks():
            full_t_name = task.name()
            t_start, t_end = task.timestamps()            

            self._data[team][user][full_t_name] = []

            for sum_toks in summaries:
                # e.g. `admin#1624217970365`
                time = sum_toks[0]
                ts = int(sum_toks[1][6:])
                elapsed = round((ts - t_start) / 1000, 2)
                action = sum_toks[2]
                values = sum_toks[3:]

                # Does it lie in this task?
                if (t_start > ts or ts > t_end):
                    continue

                
                s = SummaryPoint(action, ts, elapsed, time, values)

                self._data[team][user][full_t_name].append(s)
