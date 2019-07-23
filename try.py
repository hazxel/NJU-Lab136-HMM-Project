import os
import re


inputPath = "Z:/AchivedWorkbyName/LuSheng/MitoMoveData/trajectory"
outputPath = "C:/Users/stevenzhou/Desktop"

pattern = r"^(.*Div7MitoMove.*C - Series.*)\.xml$"

# print(re.findall(pattern, '20140711 Div7MitoMove27C - Series004.xml'))

for dirpath, _, filenames in os.walk(inputPath):
    for filename in filenames:
        if len(re.findall(pattern, filename)) > 0:
            # print(filename)
            filenames = [("{}/{}".format(dirpath, filename), 
            re.search(pattern, filename).group(2) )]

print(filenames)