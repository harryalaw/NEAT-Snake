import pygame
import random
from collections import deque

WIN_WIDTH = 600
WIN_HEIGHT = 600
GRID_WIDTH = 500  # 25 x 25 squares
GRID_HEIGHT = 500
TOP_LEFT_X = (WIN_WIDTH-GRID_WIDTH) // 2
TOP_LEFT_Y = (WIN_HEIGHT-GRID_HEIGHT) // 2
CELLWIDTH = 25
DIRECTIONS = {'Left': (-CELLWIDTH, 0), 'Right': (CELLWIDTH, 0),
              'Up': (0, -CELLWIDTH), 'Down': (0, CELLWIDTH)}


class Snake:

    def __init__(self):
        self.COLOR = (106, 238, 40)
        # @Todo assign values
        self.length = 3
        self.occupied_cells = deque()  # will store head at 0 and tail at -1
        self.occupied_cells.appendleft([125, 300])
        self.occupied_cells.appendleft([150, 300])
        self.occupied_cells.appendleft([175, 300])

        self.dir = 'Right'
        self.xvel = DIRECTIONS[self.dir][0]
        self.yvel = DIRECTIONS[self.dir][1]
        # to peek just look at occupied_cells[0]!
        #
        self.frame = 0

    def change_dir(self, dir_):
        self.dir = dir_

    def move(self):
        if self.frame % 5 != 0:
            return
        self.xvel = DIRECTIONS[self.dir][0]
        self.yvel = DIRECTIONS[self.dir][1]

        old_head = self.occupied_cells[0]
        self.occupied_cells.appendleft(
            [old_head[0]+self.xvel, old_head[1]+self.yvel])

        if len(self.occupied_cells) > self.length:
            self.occupied_cells.pop()

    def draw(self, win):
        for cell in self.occupied_cells:
            new_rect = (
                TOP_LEFT_X+cell[0], TOP_LEFT_Y+cell[1], CELLWIDTH, CELLWIDTH)
            pygame.draw.rect(win, self.COLOR, new_rect)


class Food:
    def __init__(self):
        # change this so that the points lie on the grid
        self.x = random.randint(0, WIN_WIDTH*WIN_HEIGHT-1)
        self.y = random.randint(0, WIN_WIDTH*WIN_HEIGHT-1)


def draw_window(win, snake, food):
    win.fill((0, 0, 0))
    outline = (TOP_LEFT_X, TOP_LEFT_Y, GRID_WIDTH, GRID_WIDTH)
    pygame.draw.rect(win, (255, 255, 255), outline, width=1)
    snake.draw(win)

    pygame.display.update()


def main():
    snake = Snake()

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(30)
        snake.frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    snake.change_dir('Down')
                elif event.key == pygame.K_LEFT:
                    snake.change_dir('Left')
                elif event.key == pygame.K_UP:
                    snake.change_dir('Up')
                elif event.key == pygame.K_RIGHT:
                    snake.change_dir('Right')
        snake.move()
        draw_window(win, snake, None)


main()
