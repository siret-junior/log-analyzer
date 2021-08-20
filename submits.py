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


class UserSubmits:
    def __init__(self, submits):
        self._submits = submits

    def submits(self):
        return self._submits


class Verdicts:
    def __init__(self, filepath):
        print("%%% PARSING VERDICTS %%%")

        # todo
        SUBMIT2GUID = {}
        GUID2VERDICT = {}

        print("%%% DONE %%%")

    def submit_to_verdict(self,ts, node):
        return "W"