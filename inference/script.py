#!/usr/bin/env python3

"""
This script processes the output of raw HPCG runs into a CSV dataset
"""

import os
import shutil
from glob import glob
import pandas as pd

class DataSet:
    def __init__(self, data_dir="raw", out_dir="data"):
        self.funcs = ["cg", "mg_ref", "cg_ref", "spv_ref", "cg_timed"]
        self.files = {}
        self.data = {}
        self.out_dir = out_dir
        self.data_dir = data_dir
        shutil.rmtree(self.out_dir, ignore_errors=True)
        for d in os.listdir(data_dir):
            x = os.path.join(data_dir, d)
            if os.path.isdir(x):
                self.process_dir(x)
        self.write_files()
        self.to_csv()

    def process_dir(self, d):
        for f in os.listdir(d):
            _, g = f.split("-")
            g = int(g, base=10)
            path = os.path.join(d, f)
            if "clean" in d:
                for run in os.listdir(path):
                    path = os.path.join(d, f, run)
                    for b in os.listdir(path):
                        self.process_file(os.path.join(path, b), g)
            else:
                for b in os.listdir(path):
                    self.process_file(os.path.join(path, b), g)

    def process_file(self, path, g, core=True):
        b = os.path.basename(path)
        if b.lower()[:4] != "hpcg":
            if core:
                s = b.split("_core_0_")
            else:
                s = b.split("_uncore_0_")
            func = s[0]
            err_rate = float(s[1].split("_")[0])
            inj_rate = float(s[1].split("_")[1].split(".txt")[0])
            key = (func, g, err_rate, inj_rate)
            if key in self.files:
                self.files[key].append(path)
            else:
                self.files[key] = [path]

    def write_files(self):
        os.makedirs(self.out_dir)
        for (k, v) in self.files.items():
            (func, g, err_rate, inj_rate) = k
            for i, file in enumerate(v):
                e_str = f"{err_rate:{1}.{2}f}"
                i_str = f"{inj_rate:{1}.{2}f}"
                f = f"{func}_{g}_{e_str}_{i_str}_{i}.txt"
                dst = os.path.join(self.out_dir, f)
                shutil.copyfile(file, dst)

    def to_csv(self):
        for f in self.funcs:
            for grid_size in range(1, 6):
                data = {'ErrorRate': [], "InjectionRate": []}
                grid_size = (1 << grid_size)
                for err_rate in range(0, 11):
                    err_rate /= 10
                    estr =  f"{err_rate:{1}.{2}f}"
                    for inj_rate in range(0, 11):
                        inj_rate /= 100
                        istr =  f"{inj_rate:{1}.{2}f}"
                        file = f"{f}_{grid_size}_{estr}_{istr}_*.txt"
                        files = glob(os.path.join(self.out_dir, file))
                        for file in files:
                            counters = self.read_data(file, f, err_rate, inj_rate)
                            data["ErrorRate"].append(err_rate)
                            data["InjectionRate"].append(inj_rate)
                            for k,v in counters.items():
                                if k in data:
                                    data[k].append(v)
                                else:
                                    data[k] = [v]
                df = pd.DataFrame.from_dict(data)
                title = f"{f}_{grid_size}"
                df.to_csv(os.path.join(self.out_dir, f"{title}.csv"), index=False)

    def read_data(self, file, func, err_rate, inj_rate):
        with open(file, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        counters = {}
        for line in lines:
            key, val = line.split(" ")
            if key in counters:
                raise Exception("Duplicate key found in file")
            counters[key] = int(val, base=10)
        return counters

if __name__ == "__main__":
    d = DataSet()
