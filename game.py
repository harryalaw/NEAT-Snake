import pygame
import random
from collections import deque
pygame.font.init()

SCORE_FONT = pygame.font.SysFont("Helvetica", 50)


WIN_WIDTH = 600
WIN_HEIGHT = 600
GRID_WIDTH = 500  # 25 x 25 squares
GRID_HEIGHT = 500
TOP_LEFT_X = (WIN_WIDTH-GRID_WIDTH) // 2
TOP_LEFT_Y = (WIN_HEIGHT-GRID_HEIGHT) // 2
CELLWIDTH = 25
DIRECTIONS = {'Left': (-1, 0), 'Right': (1, 0),
              'Up': (0, -1), 'Down': (0, 1)}

DISALLOWED = {'Left': 'Right', 'Up': 'Down', 'Right': 'Left', 'Down': 'Up'}


class Snake:

    def __init__(self):
        # self.COLOR = (106, 238, 40)
        self.COLOR = (random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255))
        # @Todo assign values
        self.length = 3
        self.occupied_cells = deque()  # will store head at 0 and tail at -1

        # initial setup
        self.occupied_cells.appendleft([5, 12])
        self.occupied_cells.appendleft([6, 12])
        self.occupied_cells.appendleft([7, 12])

        self.dir = 'Right'
        self.xvel = DIRECTIONS[self.dir][0]
        self.yvel = DIRECTIONS[self.dir][1]
        # to peek just look at occupied_cells[0]!

        self.score = 0
        self.frame = 0
        self.last_update = -1
        self.stored_change = None
        self.is_alive = True

    def change_dir(self, dir_):
        if self.frame == self.last_update:
            self.stored_change = dir_
            return
        if dir_ == DISALLOWED[self.dir]:
            return
        self.last_update = self.frame
        self.dir = dir_

    def move(self):
        if not self.is_alive:
            return
        # if self.frame % 2 != 0:
        #     return
        self.xvel = DIRECTIONS[self.dir][0]
        self.yvel = DIRECTIONS[self.dir][1]

        old_head = self.occupied_cells[0]
        self.occupied_cells.appendleft(
            [old_head[0]+self.xvel, old_head[1]+self.yvel])

        if len(self.occupied_cells) > self.length:
            self.occupied_cells.pop()

    def check_collision(self):
        collided = False

        curr_head = [self.occupied_cells[0][0], self.occupied_cells[0][1]]
        curr_head = self.occupied_cells.popleft()

        if curr_head[0] < 0 or curr_head[1] < 0 or curr_head[0] >= GRID_WIDTH//CELLWIDTH or curr_head[1] >= GRID_HEIGHT//CELLWIDTH:
            collided = True
        # €todo check if this is actually how the collision logic works

        elif curr_head in self.occupied_cells:
            collided = True
        self.occupied_cells.appendleft(curr_head)
        return collided

    def draw(self, win):
        for cell in self.occupied_cells:
            new_rect = (
                TOP_LEFT_X+cell[0]*CELLWIDTH, TOP_LEFT_Y+cell[1]*CELLWIDTH, CELLWIDTH, CELLWIDTH)
            pygame.draw.rect(win, self.COLOR, new_rect)

    def eat(self, food):
        if self.occupied_cells[0][0] == food.x and self.occupied_cells[0][1] == food.y:
            self.score += 1
            self.length += 1
            while [food.x, food.y] in self.occupied_cells:
                food.x = random.randint(
                    0, GRID_WIDTH//CELLWIDTH - 1)
                food.y = random.randint(
                    0, GRID_HEIGHT//CELLWIDTH - 1)


class Food:
    def __init__(self, snake):
        self.x = random.randint(0, GRID_WIDTH//CELLWIDTH - 1)
        self.y = random.randint(0, GRID_HEIGHT//CELLWIDTH - 1)

        while [self.x, self.y] in snake.occupied_cells:
            self.x = random.randint(0, GRID_WIDTH//CELLWIDTH - 1)
            self.y = random.randint(0, GRID_HEIGHT//CELLWIDTH - 1)

        # self.COLOR = (255, 0, 0)
        self.COLOR = snake.COLOR

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (TOP_LEFT_X+int((self.x+0.5)*CELLWIDTH),
                                             TOP_LEFT_Y+int((self.y+0.5)*CELLWIDTH)), CELLWIDTH//2-1)


def draw_window(win, snake, food):
    win.fill((0, 0, 0))
    outline = (TOP_LEFT_X, TOP_LEFT_Y, GRID_WIDTH, GRID_WIDTH)

    pygame.draw.rect(win, (255, 255, 255), outline, width=1)
    food.draw(win)
    snake.draw(win)

    text = SCORE_FONT.render("Score: " + str(snake.score), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    pygame.display.update()


def main():
    snake = Snake()
    food = Food(snake)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0
    while run:
        clock.tick(15)
        # using a frame
        # counter to be able to modulate the speed of the snake
        snake.frame += 1
        moved = False
        if snake.stored_change:
            snake.change_dir(snake.stored_change)
            snake.move()
            snake.stored_change = None
            moved = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    snake.change_dir('Down')
                    # snake.move()
                elif event.key == pygame.K_LEFT:
                    snake.change_dir('Left')
                    # snake.move()
                elif event.key == pygame.K_UP:
                    snake.change_dir('Up')
                    # snake.move()
                elif event.key == pygame.K_RIGHT:
                    snake.change_dir('Right')
                    # snake.move()
                # reset by pressing r
                if event.key == 114 and not snake.is_alive:
                    snake = Snake()
                    food = Food(snake)
        if not moved:
            snake.move()
        snake.eat(food)
        if snake.check_collision():
            snake.is_alive = False
        draw_window(win, snake, food)


main()