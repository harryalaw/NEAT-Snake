import pygame
import random
import neat
import os
from collections import deque

pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 600
GRID_WIDTH = 500  # 20 x 20 squares
GRID_HEIGHT = 500
TOP_LEFT_X = (WIN_WIDTH-GRID_WIDTH) // 2
TOP_LEFT_Y = (WIN_HEIGHT-GRID_HEIGHT) // 2
CELLWIDTH = 25

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
        self.occupied_cells.appendleft([5, 12])
        self.occupied_cells.appendleft([6, 12])
        self.occupied_cells.appendleft([7, 12])

        self.xvel, self.yvel = (1, 0)

        self.is_alive = True
        self.fed = False
        self.hunger = 100
        self.best_food_dist = 10000

    def turn_cw(self):
        temp = self.xvel
        self.xvel = self.yvel
        self.yvel = - temp

    def turn_ccw(self):
        temp = self.xvel
        self.xvel = - self.yvel
        self.yvel = temp

    def change_dir(self, dir_):
        value = VALID_MOVES[(self.xvel, self.yvel)][dir_]
        if value == 1:
            self.turn_cw()
        elif value == 2:
            self.turn_ccw()

    def move(self):
        if self.hunger <= 0:
            self.is_alive = False

        if not self.is_alive:
            return

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

    def draw(self, win):
        for cell in self.occupied_cells:
            new_rect = (
                TOP_LEFT_X+cell[0]*CELLWIDTH, TOP_LEFT_Y+cell[1]*CELLWIDTH, CELLWIDTH, CELLWIDTH)
            pygame.draw.rect(win, self.COLOR, new_rect)

    def eat(self, food):
        if self.occupied_cells[0][0] == food.x and self.occupied_cells[0][1] == food.y:
            self.length += 1
            self.hunger += 40
            self.fed = True
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


def draw_window(win, snakes, foods, score, gen):
    win.fill((0, 0, 0))
    outline = (TOP_LEFT_X, TOP_LEFT_Y, GRID_WIDTH, GRID_WIDTH)
    pygame.draw.rect(win, (255, 255, 255), outline, width=1)
    # food.draw(win)
    # snake.draw(win)

    for snake, food in zip(snakes, foods):
        food.draw(win)
        snake.draw(win)

    score_text = FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(score_text, (10, 10))

    gen_text = FONT.render(f"Gen: {gen}", 1, (255, 255, 255))
    win.blit(gen_text, (WIN_WIDTH - 10 - gen_text.get_width(), 10))

    pygame.display.update()


def board_to_matrix(snake, food):
    ARRAYWIDTH = GRID_WIDTH // CELLWIDTH
    ARRAYHEIGHT = GRID_HEIGHT // CELLWIDTH
    board = [[0 for _ in range(ARRAYWIDTH+2)] for _ in range(ARRAYHEIGHT+2)]
    for i in range(ARRAYWIDTH+2):
        board[0][i] = 1
        board[ARRAYHEIGHT+1][i] = 1
    for j in range(ARRAYHEIGHT+2):
        board[j][0] = 1
        board[j][ARRAYWIDTH+1] = 1
    for x, cell in enumerate(snake.occupied_cells):
        if x == 0:
            try:
                board[cell[1]][cell[0]] = 'H'
            except IndexError:
                print(f"x,y is {cell[0]}, {cell[1]}")
                for line in board:
                    print(line)
                print(f"\n {snake.occupied_cells}, alive? {snake.is_alive}")
        else:
            board[cell[1]][cell[0]] = 1
    board[food.y][food.x] = 'F'

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


def get_inputs(snake, food):
    board = board_to_matrix(snake, food)
    head = snake.occupied_cells[0]
    left_wall_dist = find_next_ray(board, 1, head, (-1, 0))
    right_wall_dist = find_next_ray(board, 1, head, (1, 0))
    up_wall_dist = find_next_ray(board, 1, head, (0, -1))
    down_wall_dist = find_next_ray(board, 1, head, (0, 1))

    x_food_dist = food.x-head[0]
    y_food_dist = food.y-head[1]

    n_food_dist = find_next_ray(board, 'F', head, (0, -1))
    ne_food_dist = find_next_ray(board, 'F', head, (1, -1))
    e_food_dist = find_next_ray(board, 'F', head, (1, 0))
    se_food_dist = find_next_ray(board, 'F', head, (1, 1))
    s_food_dist = find_next_ray(board, 'F', head, (0, 1))
    sw_food_dist = find_next_ray(board, 'F', head, (-1, 1))
    w_food_dist = find_next_ray(board, 'F', head, (-1, 0))
    nw_food_dist = find_next_ray(board, 'F', head, (-1, 1))

    inputs = [snake.xvel, snake.yvel, x_food_dist, y_food_dist,
              left_wall_dist, right_wall_dist, up_wall_dist, down_wall_dist,
              n_food_dist, ne_food_dist, e_food_dist, se_food_dist, s_food_dist, sw_food_dist, w_food_dist, nw_food_dist]
    return inputs


def food_distance(cell, food):
    """Returns the square of euclidean distance from cell to food"""
    return (cell[0] - food.x)**2 + (cell[1] - food.y)**2


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
        foods.append(Food(snakes[-1]))
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
            inputs = get_inputs(snake, foods[x])
            outputs = nets[x].activate(inputs)

            max_out = -1
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

            if snake.best_food_dist > food_distance(snake.occupied_cells[0], foods[x]):
                snake.best_food_dist = food_distance(
                    snake.occupied_cells[0], foods[x])
                ge[x].fitness += 0.5
            else:
                ge[x].fitness += 0.01

            snake.eat(foods[x])
            if snake.fed:
                ge[x].fitness += 4
                snake.fed = False

            if snake.check_collision():
                snake.is_alive = False
                ge[x].fitness -= 1
                to_rem.append(x)
            elif not snake.is_alive:
                ge[x].fitness -= 0.5
                to_rem.append(x)

            if snake.length - 3 > max_score:
                max_score = snake.length - 3

        nets = [nets[x] for x in range(len(nets)) if x not in to_rem]
        ge = [ge[x] for x in range(len(ge)) if x not in to_rem]
        snakes = [snakes[x] for x in range(len(snakes)) if x not in to_rem]
        foods = [foods[x] for x in range(len(foods)) if x not in to_rem]

        draw_window(win, snakes, foods, max_score, GEN)

# main()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
