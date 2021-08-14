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


class UserResults:
    def __init__(self, results_list):
        self._results = results_list

    def results(self):
        return self._results

    def size(self):
        return len(self._results)

class Results:
    def __init__(self):
        self._results = {}
        self._task_results = None

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
    
    def print_results(self, team, user, fr, to):
        
        for r in self._results[team][user].results():
            ts = r["timestamp"] 
            # Does it lie in this task?
            if (fr > ts or ts > to):
                continue
            
            print(r["timestamp"])
            print(r["values"])
            print("---")




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
        

