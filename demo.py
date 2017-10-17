from game_of_life import Game
import os
from random import choice

file_list = os.listdir("demo_levels/")
level_list = []
previous = ""
for i in range(len(file_list)):
    if file_list[i].endswith(".txt"):
        level_list.append(file_list[i])

while True:
    while True:
        # Loop until we find a new level
        level = choice(level_list)
        if level != previous:
            previous = level
            break
    var = Game(level).start()
    if var:
        break
