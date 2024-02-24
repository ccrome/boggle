import json
import numpy as np

r = json.load(open("solutions.json"))
boards = []
for b in r:
    boards.append((len(b['solutions']), b['solutions'], b['board']))
boards = sorted(boards, key=lambda x: x[0])
print(boards[0])
print(boards[1])
print(boards[2])
print(boards[-1])

