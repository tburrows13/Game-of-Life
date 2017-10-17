import time
import pygame

from tools import import_grid, save_grid, check_time

EXPORT_FILE = "Save"
FILE = "demo_levels/Backrake"

DEAD_COLOR = (255, 0, 0)
ALIVE_COLOR = (0, 255, 0)
CELL_SIZE = 7
GAP_SIZE = 2
UPDATE_FREQUENCY = 0.1

pygame.init()
infos = pygame.display.Info()
SCREEN_SIZE = (infos.current_w, infos.current_h - 60)



class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, state, size):
        super().__init__()
        self.width = self.height = size
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.is_alive = state
        self.redraw()
        self.to_set_alive = None

    def update(self):
        if self.to_set_alive is not None:
            self.is_alive = self.to_set_alive
            self.redraw()
            self.to_set_alive = None


    def redraw(self):
        """
        Called by Cell.update()
        """
        color = ALIVE_COLOR if self.is_alive else DEAD_COLOR
        self.image.fill(color)
        
    def kill_(self):
        """
        Don't immediately kill it. Doesn't change anything important until
        update() is called
        """
        self.to_set_alive = False

    def create(self):
        self.to_set_alive = True
    
        
class Game:
    def __init__(self, file=FILE):


        # Grid: 1 is alive, 0 is dead
        setup_grid, self.max_iter, self.update_frequency = import_grid(file if file.endswith(".txt") else file + ".txt")

        # Do some calculations with size
        total_width_gap_size = len(setup_grid[0]) * GAP_SIZE
        total_height_gap_size = len(setup_grid) * GAP_SIZE
        availible_screen_width = SCREEN_SIZE[0] - total_width_gap_size
        availible_screen_height = SCREEN_SIZE[1] - total_height_gap_size
        allowed_width = availible_screen_width // len(setup_grid[0])
        allowed_height = availible_screen_height // len(setup_grid)
        cell_size = min(allowed_width, allowed_height)
        print(cell_size)

        self.grid = [[None for _ in range(len(setup_grid[0]))]
                     for _ in range(len(setup_grid))]
        self.cell_list = pygame.sprite.Group()
        x = y = GAP_SIZE/2
        for i, row in enumerate(setup_grid):
            for j, item in enumerate(row):
                cell = Cell(x, y, item, cell_size)
                self.grid[i][j] = cell
                self.cell_list.add(cell)
                x += cell_size + GAP_SIZE
            y += cell_size + GAP_SIZE
            x = GAP_SIZE/2

        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.screen = pygame.display.set_mode((
            self.width * cell_size + self.width * GAP_SIZE,
            self.height * cell_size + self.height * GAP_SIZE))
        pygame.display.set_caption("Conway's Game of Life")

        self.paused = False

    def start(self):
        time_stamp = time.time()
        done = False
        premature_quit = True

        self.iterate()
        iterations = 1
        while done is False:
            if not self.paused:
                if self.update_frequency != 0:
                    if check_time(time_stamp, self.update_frequency):
                        time_stamp = time.time()
                        self.iterate()
                        # Check to see if we have reached the maximum iterations specified
                        if self.max_iter is not None:
                            iterations += 1
                            if iterations > self.max_iter:
                                premature_quit = False
                                break
                else:
                    self.iterate()
                    # Check to see if we have reached the maximum iterations specified
                    if self.max_iter is not None:
                        iterations += 1
                        if iterations > self.max_iter:
                            premature_quit = False
                            break

            done, premature_quit = self.process_events()
        pygame.quit()

        return premature_quit

    def iterate(self):
        for i, row in enumerate(self.grid):
            for j, item in enumerate(row):
                # Set 4 variables to check if we are on the edges
                top = i == 0
                bottom = i == self.height - 1
                left = j == 0
                right = j == self.width - 1

                adjacent_cells = 0
                if not top and not left and self.grid[i-1][j-1].is_alive:
                    adjacent_cells += 1
                if not top and self.grid[i-1][j].is_alive:  # Up
                    adjacent_cells += 1
                if not top and not right and self.grid[i-1][j+1].is_alive:
                    adjacent_cells += 1
                if not right and self.grid[i][j+1].is_alive:
                    adjacent_cells += 1
                if not right and not bottom and self.grid[i+1][j+1].is_alive:
                    adjacent_cells += 1
                if not bottom and self.grid[i+1][j].is_alive:
                    adjacent_cells += 1
                if not bottom and not left and self.grid[i+1][j-1].is_alive:
                    adjacent_cells += 1
                if not left and self.grid[i][j-1].is_alive:
                    adjacent_cells += 1

                # Apply the 4 rules
                if item.is_alive and (adjacent_cells < 2 or adjacent_cells > 3):
                    # Die if to many or too few adjacent
                    item.kill_()
                    
                elif not item.is_alive and adjacent_cells == 3:
                    # Born if 3 cells adjacent
                    item.create()
                    
        self.cell_list.update()
        self.cell_list.draw(self.screen)
        pygame.display.flip()

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True, True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True, True

                elif event.key == pygame.K_SPACE:
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                elif event.key == pygame.K_e:
                    self.save()
                elif event.key == pygame.K_RETURN:
                    return True, False

        return False, False

    def save(self):
        export_grid = []
        for line in self.grid:
            new_line = ""
            for cell in line:
                new_line += str(1 if cell.is_alive else 0)
            export_grid.append(new_line)
        save_grid(EXPORT_FILE + ".txt", export_grid)


if __name__ == "__main__":
    """
    Any live cell with fewer than two live neighbours dies, as if caused by underpopulation.
    Any live cell with two or three live neighbours lives on to the next generation.
    Any live cell with more than three live neighbours dies, as if by overpopulation.
    Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
    """
    game = Game()
    game.start()
