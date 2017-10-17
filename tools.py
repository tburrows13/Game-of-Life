import time


def import_grid(file_to_open):
    grid = []
    print(file_to_open)
    with open("demo_levels/" + file_to_open) as file:
        for i, line in enumerate(file):
            if i == 0:
                iterations = int(line.split(" ")[0])
                delay = float(line.split(" ")[1])
            else:
                grid.append([])
                line = line.strip()
                for item in line:
                    grid[i-1].append(int(item))

    return grid, iterations, delay


def save_grid(file, grid):
    with open(file, 'w') as file:
        for line in grid:
            file.write(line + "\n")


def check_time(prev_time, freq):
    if time.time() - prev_time > freq:
        return True
    else:
        return False
