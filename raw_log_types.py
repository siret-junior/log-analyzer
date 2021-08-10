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

