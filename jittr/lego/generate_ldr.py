#!/usr/bin/env python

import sys

try:
    file = open("partlist_bl")
except IOError:
    sys.exit("no file")

ldr_file = open("parts.ldr", 'w')
lines = file.readlines()
part_numbers = []
part_colours = []
parts = []
colours = {'Blue': 1, 'Added': 7, '(Inv)': 7, 'Light': 7, 'Trans-Clear': 47, 'Yellow': 14, 'Metallic': 80, 'Dark': 8, 'Trans-Red': 36, 'Black': 0, 'Trans-Black': 40, 'Orange': 25, 'White': 15, 'Trans-Yellow': 46, 'Tan': 19, 'Red': 4}
colours_new = {}


for line in lines:
    words = line.split()
    if words[0] == 'Yes':
        num = words[2]
        col = words[3]
        if col not in colours:
            colours[col] = input("%s: " % col)
            colours_new[col] = colours[col]
        if num not in part_numbers:
            part_numbers.append(num)
            part_colours.append(colours[col])
            parts.append((num, colours[col]))

print ("There are %s parts, with %s colours \n" % (len(parts), len(colours))) 

output_lines = []

for part in parts:
    line = "1 %s 0 0 0 1 0 0 0 1 0 0 0 1 %s.dat\n" % (part[1], part[0])
    output_lines.append(line)

ldr_file.writelines(output_lines)

