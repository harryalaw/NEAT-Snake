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
        self.length = 20
        self.occupied_cells = deque()  # will store head at 0 and tail at -1
        self.occupied_cells.appendleft([125, 300])
        self.occupied_cells.appendleft([150, 300])
        self.occupied_cells.appendleft([175, 300])

        self.dir = 'Right'
        self.xvel = DIRECTIONS[self.dir][0]
        self.yvel = DIRECTIONS[self.dir][1]
        # to peek just look at occupied_cells[0]!

        self.frame = 0
        self.is_alive = True

    def change_dir(self, dir_):
        self.dir = dir_

    def move(self):
        # @todo disallow moving back onto itself.
        # @todo implement a queue system to the inputs, so that one press corresponds to one movement
        if not self.is_alive:
            return
        if self.frame % 2 != 0:
            return
        self.xvel = DIRECTIONS[self.dir][0]
        self.yvel = DIRECTIONS[self.dir][1]

        old_head = self.occupied_cells[0]
        self.occupied_cells.appendleft(
            [old_head[0]+self.xvel, old_head[1]+self.yvel])

        if len(self.occupied_cells) > self.length:
            self.occupied_cells.pop()

        # collision logic:
        self.check_collision()

    def check_collision(self):
        collided = False

        next_head = [self.occupied_cells[0][0] +
                     self.xvel, self.occupied_cells[0][1]+self.yvel]
        if next_head[0] < 0 or next_head[1] < 0 or next_head[0] >= GRID_WIDTH or next_head[1] >= GRID_HEIGHT:
            collided = True
        # €todo check if this is actually how the collision logic works
        elif next_head in self.occupied_cells and next_head != self.occupied_cells[-1]:
            collided = True
        return collided

    def draw(self, win):
        for cell in self.occupied_cells:
            new_rect = (
                TOP_LEFT_X+cell[0], TOP_LEFT_Y+cell[1], CELLWIDTH, CELLWIDTH)
            pygame.draw.rect(win, self.COLOR, new_rect)

    def eat(self, food):
        if self.occupied_cells[0][0] == food.x and self.occupied_cells[0][1] == food.y:
            self.length += 1
            while [food.x, food.y] in self.occupied_cells:
                food.x = random.randint(
                    0, GRID_WIDTH//CELLWIDTH - 1) * CELLWIDTH
                food.y = random.randint(
                    0, GRID_HEIGHT//CELLWIDTH - 1) * CELLWIDTH


class Food:
    def __init__(self, snake):
        self.x = random.randint(0, GRID_WIDTH//CELLWIDTH - 1) * CELLWIDTH
        self.y = random.randint(0, GRID_HEIGHT//CELLWIDTH - 1) * CELLWIDTH

        while [self.x, self.y] in snake.occupied_cells:
            self.x = random.randint(0, GRID_WIDTH//CELLWIDTH - 1) * CELLWIDTH
            self.y = random.randint(0, GRID_HEIGHT//CELLWIDTH - 1) * CELLWIDTH

        self.color = (255, 0, 0)

    def draw(self, win):
        pygame.draw.circle(win, self.color, (TOP_LEFT_X+self.x+CELLWIDTH //
                                             2, TOP_LEFT_Y+self.y+CELLWIDTH//2), CELLWIDTH//2-1)


def draw_window(win, snake, food):
    win.fill((0, 0, 0))
    outline = (TOP_LEFT_X, TOP_LEFT_Y, GRID_WIDTH, GRID_WIDTH)
    pygame.draw.rect(win, (255, 255, 255), outline, width=1)
    food.draw(win)
    snake.draw(win)

    pygame.display.update()


def main():
    snake = Snake()
    food = Food(snake)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(30)
        # using a frame counter to be able to modulate the speed of the snake
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
        if snake.frame % 2 == 0:
            snake.move()
            snake.eat(food)
            if snake.check_collision():
                snake.is_alive = False
        draw_window(win, snake, food)


main()
