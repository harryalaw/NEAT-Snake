import pygame
import random
import numpy as np
from collections import deque

pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 600
GRID_WIDTH = 250  # 25 x 25 squares
GRID_HEIGHT = 250
TOP_LEFT_X = (WIN_WIDTH-GRID_WIDTH) // 2
TOP_LEFT_Y = (WIN_HEIGHT-GRID_HEIGHT) // 2
CELLWIDTH = 25
LOWER = 3
UPPER = GRID_WIDTH//CELLWIDTH - 4

# Key to remember what the
# DIRECTIONS = {'Left': (-1, 0), 'Right': (1, 0),
#               'Up': (0, -1), 'Down': (0, 1)}

# 0 => Do nothing, 1 => Turn clockwise, 2 => turn counterclockwise, -1 => Ignore
# VALID_MOVES = {'Up': {'Up': 0, 'Left': 1, 'Right': 2, 'Down': -1},
#                'Left': {'Up': 2, 'Left': 0, 'Right': -1, 'Down': 1},
#                'Down': {'Up': -1, 'Left': 2, 'Right': 1, 'Down': 0},
#                'Right': {'Up': 1, 'Left': -1, 'Right': 0, 'Down': 2}
#                }
VALID_MOVES = {(0, -1): {(0, -1): 0, (-1, 0): 1, (1, 0): 2, (0, 1): -1},
               (-1, 0): {(0, -1): 2, (-1, 0): 0, (1, 0): -1, (0, 1): 1},
               (0, 1): {(0, -1): -1, (-1, 0): 2, (1, 0): 1, (0, 1): 0},
               (1, 0): {(0, -1): 1, (-1, 0): -1, (1, 0): 0, (0, 1): 2}
               }

FONT = pygame.font.SysFont("comicsans", 50)


class Snake:

    def __init__(self):
        # self.COLOR = (106, 238, 40)
        self.COLOR = (random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255))

        self.length = 3
        self.occupied_cells = deque()  # will store head at 0 and tail at -1

        # initial setup
        # self.occupied_cells.appendleft([5, 12])
        # self.occupied_cells.appendleft([6, 12])
        # self.occupied_cells.appendleft([7, 12])

        # self.xvel, self.yvel = (1, 0)

        # initial setup
        self.occupied_cells.appendleft(
            [random.randint(LOWER, UPPER), random.randint(LOWER, UPPER)])

        dir_ = random.randint(0, 3)
        moves = ((-1, 0), (1, 0), (0, -1), (0, 1))

        self.xvel, self.yvel = moves[dir_]
        for i in range(2):
            x, y = self.occupied_cells[0]
            x += self.xvel
            y += self.yvel
            self.occupied_cells.appendleft((x, y))

        self.frame = 0
        self.last_update = -1
        self.stored_change = None
        self.is_alive = True

    def turn_cw(self):
        temp = self.xvel
        self.xvel = self.yvel
        self.yvel = - temp

    def turn_ccw(self):
        temp = self.xvel
        self.xvel = - self.yvel
        self.yvel = temp

    def change_dir(self, dir_):
        if self.frame == self.last_update:
            self.stored_change = dir_
            return
        self.last_update = self.frame
        value = VALID_MOVES[(self.xvel, self.yvel)][dir_]
        if value == 1:
            self.turn_cw()
        elif value == 2:
            self.turn_ccw()

    def move(self):
        if not self.is_alive:
            return

        old_head = self.occupied_cells[0]
        self.occupied_cells.appendleft(
            [old_head[0]+self.xvel, old_head[1]+self.yvel])

        if len(self.occupied_cells) > self.length:
            self.occupied_cells.pop()

    def check_collision(self):
        collided = False

        curr_head = [self.occupied_cells[0][0], self.occupied_cells[0][1]]
        # curr_head = self.occupied_cells.popleft()

        if curr_head[0] < 0 or curr_head[1] < 0 or curr_head[0] >= GRID_WIDTH//CELLWIDTH or curr_head[1] >= GRID_HEIGHT//CELLWIDTH:
            collided = True

        elif curr_head in list(self.occupied_cells)[1:]:
            collided = True
        # self.occupied_cells.appendleft(curr_head)
        return collided

    def draw(self, win):
        for cell in self.occupied_cells:
            new_rect = (
                TOP_LEFT_X+cell[0]*CELLWIDTH, TOP_LEFT_Y+cell[1]*CELLWIDTH, CELLWIDTH, CELLWIDTH)
            pygame.draw.rect(win, self.COLOR, new_rect)

    def eat(self, food):
        if self.occupied_cells[0][0] == food.x and self.occupied_cells[0][1] == food.y:
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

        self.COLOR = snake.COLOR

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (TOP_LEFT_X+int((self.x+0.5)*CELLWIDTH),
                                             TOP_LEFT_Y+int((self.y+0.5)*CELLWIDTH)), CELLWIDTH//2-1)


def draw_window(win, snake, food, score):
    win.fill((0, 0, 0))
    outline = (TOP_LEFT_X, TOP_LEFT_Y, GRID_WIDTH, GRID_WIDTH)
    pygame.draw.rect(win, (255, 255, 255), outline, width=1)
    food.draw(win)
    snake.draw(win)

    score_text = FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(score_text, (10, 10))

    pygame.display.update()

    board = board_to_matrix(snake, food)
    for line in board:
        for char in line:
            print(char, end=' ')
        print()
    print()
    search_board_ray(board, snake.occupied_cells[0], (1, 0))
    search_board_ray(board, snake.occupied_cells[0], (1, 1))
    search_board_ray(board, snake.occupied_cells[0], (0, 1))
    search_board_ray(board, snake.occupied_cells[0], (-1, 1))
    search_board_ray(board, snake.occupied_cells[0], (-1, 0))
    search_board_ray(board, snake.occupied_cells[0], (-1, -1))
    search_board_ray(board, snake.occupied_cells[0], (0, -1))
    search_board_ray(board, snake.occupied_cells[0], (1, -1))


def board_to_matrix(snake, food):
    """Converts a snake game into a matrix.
    Outer edges are denoted by 'W'
    Snake head by 'H' and body by '1'
    Food by 'F'"""

    ARRAYWIDTH = GRID_WIDTH // CELLWIDTH
    ARRAYHEIGHT = GRID_HEIGHT // CELLWIDTH
    board = [[0 for _ in range(ARRAYWIDTH+2)] for _ in range(ARRAYHEIGHT+2)]
    for i in range(ARRAYWIDTH+2):
        board[0][i] = 'W'
        board[ARRAYHEIGHT+1][i] = 'W'
    for j in range(ARRAYHEIGHT+2):
        board[j][0] = 'W'
        board[j][ARRAYWIDTH+1] = 'W'
    for x, cell in enumerate(snake.occupied_cells):
        if x == 0:
            board[cell[1]+1][cell[0]+1] = 'H'
        else:
            board[cell[1]+1][cell[0]+1] = 1
    board[food.y+1][food.x+1] = 'F'
    return board


def find_next_ray(board, object, start, ray):
    """Finds the next instance of {object} in direction {ray} 
    starting from {start} and returns the square of the 
    euclidean distance or -1 if {object} not found"""
    x, y = start

    while True:
        if x < 0 or y < 0 or x >= len(board[0]) or y >= len(board):
            return -1
        if board[y][x] == object:
            return (x-start[0])**2 + (y-start[1])**2
        else:
            x += ray[0]
            y += ray[1]


def search_board_ray(board, start, ray):
    """Searches through the board in a direction {ray} and notes the distance to a body cell, if food lies on the ray and the distance to the wall"""

    x, y = start[0] + 1, start[1]+1
    food_found = False
    # body_found = False
    body_distance = np.inf
    distance = 0
    while True:
        if x < 0 or y < 0 or x >= len(board[0]) or y >= len(board):
            break
        elif board[y][x] == 'F':
            food_found = True
        elif board[y][x] == 1:
            if distance < body_distance:
                body_distance = distance
                # body_found = True
        elif board[y][x] == 'W':
            break
        distance += 1
        x += ray[0]
        y += ray[1]

    # @TODO FIGURE OUT WHY THIS IS DIVIDING BY 0 I think the issue is in the initialisation of the board
    body_distance = 1.0/body_distance
    distance = 1.0/distance
    print(
        f"Direction: {ray}, Distance: {distance}, body: {body_distance}, food: {food_found}")
    return (body_distance, food_found, distance)


def main():
    snake = Snake()
    food = Food(snake)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0
    while run:
        clock.tick(15)
        # counter to be able to modulate the speed of the snake
        snake.frame += 1

        start_length = snake.length
        moved = False
        temp_dir = None

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
                    temp_dir = (0, 1)
                    snake.change_dir(temp_dir)
                    snake.move()
                    snake.eat(food)
                    draw_window(win, snake, food, score)
                elif event.key == pygame.K_LEFT:
                    temp_dir = (-1, 0)
                    snake.change_dir(temp_dir)
                    snake.move()
                    snake.eat(food)
                    draw_window(win, snake, food, score)
                elif event.key == pygame.K_UP:
                    temp_dir = (0, -1)
                    snake.change_dir(temp_dir)
                    snake.move()
                    snake.eat(food)
                    draw_window(win, snake, food, score)
                elif event.key == pygame.K_RIGHT:
                    temp_dir = (1, 0)
                    snake.change_dir(temp_dir)
                    snake.move()
                    snake.eat(food)
                    draw_window(win, snake, food, score)

                # reset by pressing r
                if event.key == 114 and not snake.is_alive:
                    snake = Snake()
                    food = Food(snake)
                    score = 0

        # if temp_dir:
        #     snake.change_dir(temp_dir)

        # if not moved:
        #     snake.move()

        # snake.eat(food)

        if snake.check_collision():
            snake.is_alive = False

        if snake.length > start_length:
            score += 1

        # draw_window(win, snake, food, score)
        board = board_to_matrix(snake, food)


main()
