"""
Author: Paco Kwon
this python script is used to filter inappropriate directory
names that contain ".mp3" at the end of their names so that
my music player can operate without trouble
"""

import os
import json
# /mnt/WindowsDrive/Users/haech/Music

with open("config.json") as f:
    data = json.load(f)

root = data["root"]
bad_names = []
for dirName, subdirList, fileList in os.walk(root):
    print(dirName)
    if dirName.endswith(".mp3"):
        bad_names.append(dirName)

for n in bad_names:
    os.rename(n, n[:-4])
