%%
import pandas as pd
import pathlib as pb
from datetime import date
from collections import defaultdict

p = pb.Path(".")
all_jsons = list(p.glob("**/*.json"))
#getting list of all dates from filenames
all_jsons = [i.stem.split("_") for i in all_jsons if "_" in i.name]
#writing them to dictionary client: [dates]
dic = defaultdict(list)
for name,dt in all_jsons:
    dic[name].append(dt)
#getting max date for every client    
for key in dic:
    dic[key] = str(sorted([date.fromisoformat(i) for i in dic[key]])[-1])
#constructing the names corresponding to max date
names = [key + "_" + val + ".json" for key,val in dic.items()]

print(names)
df = pd.read_json("")