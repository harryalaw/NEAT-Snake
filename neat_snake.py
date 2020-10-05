import pygame
import random
import neat
import os
import numpy as np
from collections import deque

pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 600
GRID_WIDTH = 250  # 20 x 20 squares
GRID_HEIGHT = 250
TOP_LEFT_X = (WIN_WIDTH-GRID_WIDTH) // 2
TOP_LEFT_Y = (WIN_HEIGHT-GRID_HEIGHT) // 2
CELLWIDTH = 25

LOWER = 4
UPPER = 6
GEN = 0
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
        self.occupied_cells.appendleft(
            [random.randint(LOWER, UPPER), random.randint(LOWER, UPPER)])

        dir_ = random.randint(0, 3)
        moves = ((-1, 0), (1, 0), (0, -1), (0, 1))

        # initialised to these values so that after it moves two steps
        # when I create it's start point it will start with 0 steps
        # and 100 hunger
        self.steps = -2
        self.hunger = 102
        self.is_alive = True
        self.fed = False

        self.food = Food(self)

        self.xvel, self.yvel = moves[dir_]
        for i in range(2):
            self.move()

    def turn_cw(self):
        temp = self.xvel
        self.xvel = self.yvel
        self.yvel = - temp

    def turn_ccw(self):
        temp = self.xvel
        self.xvel = - self.yvel
        self.yvel = temp

    def change_dir(self, dir_):
        # value = VALID_MOVES[(self.xvel, self.yvel)][dir_]
        # if value == 1:
        #     self.turn_cw()
        # elif value == 2:
        #     self.turn_ccw()
        self.xvel = dir_[0]
        self.yvel = dir_[1]

    def move(self):
        if self.hunger <= 0:
            self.is_alive = False

        if not self.is_alive:
            return

        self.steps += 1
        self.hunger -= 1

        old_head = self.occupied_cells[0]
        self.occupied_cells.appendleft(
            [old_head[0]+self.xvel, old_head[1]+self.yvel])

        if len(self.occupied_cells) > self.length:
            self.occupied_cells.pop()

    def check_collision(self):
        collided = False
        curr_head = [self.occupied_cells[0][0], self.occupied_cells[0][1]]

        if curr_head[0] < 0 or curr_head[1] < 0 or curr_head[0] >= GRID_WIDTH//CELLWIDTH or curr_head[1] >= GRID_HEIGHT//CELLWIDTH:
            self.is_alive = False
            collided = True
        elif curr_head in list(self.occupied_cells)[1:]:
            self.is_alive = False
            collided = True
        return collided

    def eat(self):
        if self.occupied_cells[0][0] == self.food.x and self.occupied_cells[0][1] == self.food.y:
            self.length += 1
            self.hunger += 100
            self.fed = True
            while [self.food.x, self.food.y] in self.occupied_cells:
                self.food.x = random.randint(
                    0, GRID_WIDTH//CELLWIDTH - 1)
                self.food.y = random.randint(
                    0, GRID_HEIGHT//CELLWIDTH - 1)

    def eval_fitness(self):
        food_eaten = self.length - 3
        steps = self.steps
        A, B, C, D, E, F = 2, 2.1, 500, 1.2, 0.25, 1.3
        # changed this formula to punish steps harder
        # formula is taken from https://github.com/Chrispresso/SnakeAI
        return steps + ((A**food_eaten) + (food_eaten**B) * C) - (((food_eaten+1)**D) * ((E*steps)**F))

    def draw(self, win):
        for cell in self.occupied_cells:
            new_rect = (
                TOP_LEFT_X+cell[0]*CELLWIDTH, TOP_LEFT_Y+cell[1]*CELLWIDTH, CELLWIDTH, CELLWIDTH)
            pygame.draw.rect(win, self.COLOR, new_rect)


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


def draw_window(win, snakes, score, gen):
    win.fill((0, 0, 0))
    outline = (TOP_LEFT_X, TOP_LEFT_Y, GRID_WIDTH, GRID_WIDTH)
    pygame.draw.rect(win, (255, 255, 255), outline, width=1)

    for snake in snakes:
        snake.food.draw(win)
        snake.draw(win)

    score_text = FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(score_text, (10, 10))

    gen_text = FONT.render(f"Gen: {gen}", 1, (255, 255, 255))
    win.blit(gen_text, (WIN_WIDTH - 10 - gen_text.get_width(), 10))

    pygame.display.update()


def board_to_matrix(snake):
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
    board[snake.food.y+1][snake.food.x+1] = 'F'

    return board


def search_board_ray(board, start, ray):
    """Searches through the board in a direction {ray} and notes the distance to a body cell, if food lies on the ray and the distance to the wall"""

    x, y = start[0] + 1, start[1]+1
    food_found = False
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
        elif board[y][x] == 'W':
            break
        distance += 1
        x += ray[0]
        y += ray[1]

    try:
        body_distance = 1.0/body_distance
    except ZeroDivisionError:
        print(x, y, body_distance)
        for line in board:
            for char in line:
                print(char, end=' ')
            print()
    distance = 1.0/distance
    return (body_distance, food_found, distance)


def get_inputs(snake):
    """Gets inputs in 8 directions(n, ne, e, se, s, sw, w, nw) and checks for distance to:
        Food, Walls, and other body parts
        Also gets input of what direction the snake currently has
        and the direction of its tail"""
    board = board_to_matrix(snake)
    head = snake.occupied_cells[0]
    next_tail = snake.occupied_cells[-2]
    tail = snake.occupied_cells[-1]

    tail_vel = (next_tail[0]-tail[0], next_tail[1]-tail[1])

    n_self_dist, n_food_found, n_wall_dist = search_board_ray(
        board, head, (0, -1))
    ne_self_dist, ne_food_found, ne_wall_dist = search_board_ray(
        board, head, (1, -1))
    e_self_dist, e_food_found, e_wall_dist = search_board_ray(
        board, head, (1, 0))
    se_self_dist, se_food_found, se_wall_dist = search_board_ray(
        board, head, (1, 1))
    s_self_dist, s_food_found, s_wall_dist = search_board_ray(
        board, head, (0, 1))
    sw_self_dist, sw_food_found, sw_wall_dist = search_board_ray(
        board, head, (-1, 1))
    w_self_dist, w_food_found, w_wall_dist = search_board_ray(
        board, head, (-1, 0))
    nw_self_dist, nw_food_found, nw_wall_dist = search_board_ray(
        board, head, (-1, 1))

    inputs = [
        n_wall_dist, ne_wall_dist, e_wall_dist, se_wall_dist, s_wall_dist, sw_wall_dist, w_wall_dist, nw_wall_dist,
        n_self_dist, ne_self_dist, e_self_dist, se_self_dist, s_self_dist, sw_self_dist, w_self_dist, nw_self_dist,
        n_food_found, ne_food_found, e_food_found, se_food_found, s_food_found, sw_food_found, w_food_found, nw_food_found,
        snake.xvel, snake.yvel, tail_vel[0], tail_vel[1]
    ]
    return inputs


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    snakes = []
    foods = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        snakes.append(Snake())
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    max_score = 0

    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(snakes) == 0:
            run = False
            break

        to_rem = []
        for x, snake in enumerate(snakes):
            inputs = get_inputs(snake)
            outputs = nets[x].activate(inputs)

            max_out = 0.8
            ind = -1
            for index, out in enumerate(outputs):
                if out > max_out:
                    max_out = out
                    ind = index

            if ind == 0:
                # left
                snake.change_dir((-1, 0))
            elif ind == 1:
                # right
                snake.change_dir((1, 0))
            elif ind == 2:
                # up
                snake.change_dir((0, -1))
            elif ind == 3:
                # down
                snake.change_dir((0, 1))

            snake.move()

            snake.eat()
            if snake.fed:
                snake.fed = False

            ge[x].fitness = snake.eval_fitness()

            if snake.check_collision() or not snake.is_alive:
                snake.is_alive = False
                to_rem.append(x)

            if snake.length - 3 > max_score:
                max_score = snake.length - 3

        nets = [nets[x] for x in range(len(nets)) if x not in to_rem]
        ge = [ge[x] for x in range(len(ge)) if x not in to_rem]
        snakes = [snakes[x] for x in range(len(snakes)) if x not in to_rem]

        draw_window(win, snakes, max_score, GEN)

# main()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
