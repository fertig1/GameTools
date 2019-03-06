"""
Copyright (C) 2014 Stanislav Bobovych

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import division
from __future__ import print_function

from builtins import zip
from past.utils import old_div
import argparse
import os
import re
import matplotlib.pyplot as plt
import sys

parser = argparse.ArgumentParser(description='Tool that recursively scans directories and visualizes file sizes.', \
                                epilog='')

parser.add_argument('path', nargs='?', help='Root directory to scan.')
parser.add_argument('--filt', default='', help='Regex expression used to filter out directories or files.')
parser.add_argument('--ext-only', default=False, action='store_true', help='Only do file extension analysis')

args = parser.parse_args()
path = args.path
filt = re.compile(args.filt)

num_files = 0
total_size = 0
file_dict = {}
ext_dict = {}
for root, dir, files in os.walk(path):
    if re.search(filt, root) == None or args.filt == '':
        for f in files:
            fpath = os.path.join(root,f)
            fsize = os.path.getsize(fpath)
            if not args.ext_only:

                num_files += 1
                total_size += fsize
                file_dict[fpath] = fsize

            ext = os.path.splitext(f)[1]
            if ext in ext_dict:
                ext_dict[ext] = [ext_dict[ext][0] + 1, ext_dict[ext][1] + fsize]
            else:
                ext_dict[ext] = (1, fsize)

for key,item in list(ext_dict.items()):
    print("{0:10}\t{1:10}\t{2:10}".format(key, item[0], int(old_div(item[1],item[0]))))

if not args.ext_only:    
    files_counts = sorted(list(file_dict.items()), key=lambda x:x[1], reverse=True)     # list of tuples (path, size)
    paths,sizes = list(zip(*files_counts))

    # plotting
    labels = list([os.path.basename(x) for x in paths])
    plt.figure(1, figsize=(6,6))
    plt.ax = plt.axes([0.1, 0.1, 0.8, 0.8])
    plt.pie(sizes, labels=labels)
    plt.title("Directory: %s, file count: %s, total size(mb): %s" % (path, num_files, old_div(total_size,1024)))
    plt.show()
