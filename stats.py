#!/usr/bin/env python3

import os
import sys
import glob
import json
import numpy as np
import scipy as sp
import scipy.stats
from matplotlib import pyplot as plt
from prettytable import PrettyTable

def usage():
    print("Usage: ./stats.py old_dir new_dir")
    sys.exit(0)
if len(sys.argv) != 3:
    usage()
if (not os.path.exists(sys.argv[1])) or (not os.path.exists(sys.argv[2])):
    usage()

folder_new = sys.argv[1]
folder_old = sys.argv[2]

files_new = glob.glob(os.path.join(folder_new, '*.json'))
files_old = glob.glob(os.path.join(folder_old, '*.json'))

def load(src):
    tmp = {}
    for filename in src:
        with open(filename, 'r') as f:
            tmp[filename.split('/')[-1].split('.')[0]] = (lambda x: np.asarray([[i,x[i]] for i in sorted(x.keys())], dtype=np.double))(json.load(f)['data'])
    return tmp.copy()

new, old = [load(x) for x in [files_new, files_old]]

blacklist = ['18-19-20-21 Riser Return']  # ignore

correspondences = sorted([x for x in set(new.keys()) if x in set(old.keys()) and not x in set(blacklist)])

print("Out of {} old sensors and {} new sensors, found {} sensors common between datasets: ".format(len(old.keys()), len(new.keys()), len(correspondences)))
for c in correspondences:
    print(c)

def getStats(t, y):
    mean = np.mean(y);
    stddev = np.std(y);
    return {'mean': mean, 'stddev': stddev}

stats = {}

correspondences = correspondences[::-1]

n_groups = len(correspondences)

table = PrettyTable()
table.field_names = ["Sensor", "Old mean", "New mean", "% change", "Old stddev", "New stddev"]


for c in correspondences:
    if c not in stats.keys():
        stats[c] = {}

    stats[c]['new'] = getStats(*new[c].T)
    stats[c]['old'] = getStats(*old[c].T)
    stats[c]['combined'] = getStats(*np.vstack([new[c], old[c]]).T)

correspondences = sorted(correspondences, key=lambda c: 100*(stats[c]['new']['mean']-stats[c]['old']['mean'])/stats[c]['old']['mean'])

for c in correspondences:
    table.add_row([ c,
                   round(stats[c]['old']['mean'], 3),
                   round(stats[c]['new']['mean'], 3),
                   round(100*(stats[c]['new']['mean']-stats[c]['old']['mean'])/stats[c]['old']['mean'], 3),
                   round(stats[c]['old']['stddev'], 3),
                   round(stats[c]['new']['stddev'], 3)
                   ])

print(table)

q = lambda a, b : np.asarray([stats[c][a][b] for c in correspondences])

index = np.arange(n_groups)*1.25
bar_width = 0.50
plt.barh(index, q('new','mean'), bar_width ,color='tab:blue')
plt.barh(index+bar_width, q('old','mean'), bar_width,color='tab:orange')
plt.errorbar(q('new','mean'), index, xerr=q('new','stddev'),fmt='none',barsabove=True,ecolor='tab:grey')
plt.errorbar(q('old','mean'), index+bar_width, xerr=q('old','stddev'),fmt='none',barsabove=True,ecolor='tab:grey')
plt.yticks(index+bar_width, correspondences)
plt.ylabel("Sensor")
plt.xlabel("Average temperature (F)")
plt.xlim([55, 155])
plt.legend(['Dev (Apr 22–30)','Prod (May 4–11)'])
plt.title("Dev vs. Prod average temperatures")
plt.tight_layout()

plt.show()

index = np.arange(n_groups)
bar_width = 0.40
plt.close()
plt.barh(index, 100*(q('new','mean')-q('old','mean'))/q('old','mean'), color='tab:blue')
plt.errorbar(100*(q('new','mean')-q('old','mean'))/q('old','mean'),index, xerr=q('combined','stddev'),fmt='none',barsabove=True,ecolor='tab:gray')
plt.xlabel("Percent difference")
plt.ylabel("Sensor")
plt.yticks(index, correspondences)
plt.xlim([-35, 35])
plt.title("Prod percent change in avg temp")
#plt.legend(['Dev (Apr 22–30)','Prod (May 4–11)'])
plt.tight_layout()
plt.show()


