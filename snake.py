import pygame
from random import randint

HEIGHT = WIDTH = 600
MAP_SIZE = 20
BLOCK_SIZE = int(HEIGHT / MAP_SIZE)
WINDOW = pygame.display.set_mode((HEIGHT, WIDTH))
pygame.display.set_caption("Snake")

CLOCK = pygame.time.Clock()

GRID_COLOR = (128, 128, 128)
SNAKE_COLOR = (100, 255, 100)
FRUIT_COLOR = (255, 100, 100)
BG_COLOR = (64, 64, 64)
LIGHTER_BG_COLOR = (192, 192, 192)
TEXT_COLOR = (0, 0, 0)

MOVEMENTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class SnakeNode:
    def __init__(self, pos):
        self.pos: list[int] = pos
        self.next: SnakeNode = None

    def collides(self, other, direction):
        return self.pos[0] + direction[0] == other.pos[0] and self.pos[1] + direction[1] == other.pos[1]
    
    def eats(self, fruit, direction):
        x_aux = self.pos[0] + direction[0] if 0 <= self.pos[0] + direction[0] < MAP_SIZE else (MAP_SIZE - 1 if self.pos[0] <= 0 else 0)
        y_aux = self.pos[1] + direction[1] if 0 <= self.pos[1] + direction[1] < MAP_SIZE else (MAP_SIZE - 1 if self.pos[1] <= 0 else 0) 
        return x_aux == fruit[0] and y_aux == fruit[1]

    def draw(self):
        pygame.draw.rect(WINDOW, SNAKE_COLOR, (self.pos[0] * BLOCK_SIZE, self.pos[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    def move(self, dist):
        self.pos[0] += dist[0]
        self.pos[1] += dist[1]

class SnakeCircularLinkedList:
    def __init__(self):
        self.head = SnakeNode([0, 2])
        self.tail = self.head
        self.head.next = self.head
        self.size_attr = 1

    def append(self, pos):
        new_node = SnakeNode(pos)
        self.head.next = new_node
        new_node.next = self.tail
        self.tail = new_node
        self.size_attr += 1

    def move(self, direction, ate):
        current = self.tail
        tail_pos = self.tail.pos.copy()
        while current is not self.head:
            current.pos = current.next.pos.copy()
            current = current.next
        if ate:
            self.append(tail_pos)
        self.head.pos[0] += direction[0]
        self.head.pos[1] += direction[1]
        if self.head.pos[0] >= MAP_SIZE: self.head.pos[0] = 0
        if self.head.pos[0] < 0: self.head.pos[0] = MAP_SIZE - 1
        if self.head.pos[1] >= MAP_SIZE: self.head.pos[1] = 0
        if self.head.pos[1] < 0: self.head.pos[1] = MAP_SIZE - 1

    def draw(self):
        self.head.draw()
        current = self.head.next
        while current is not self.head:
            current.draw()
            current = current.next

    def collides(self):
        aux = self.head.next
        while aux is not self.head:
            if self.head.collides(aux, [0, 0]):
                return True
            aux = aux.next
        return False

    def is_empty(self, pos):
        aux = self.head.next
        while aux is not self.head:
            if self.head.pos[0] == pos[0] and self.head.pos[1] == pos[1]:
                return False
            aux = aux.next
        return True
        
def draw_grid():
    for x in range(WIDTH // BLOCK_SIZE):
        for y in range(HEIGHT // BLOCK_SIZE):
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE,
                               BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(WINDOW, GRID_COLOR, rect, 1)


def update(snake, fruit, direction, cooldown):
    cooldown[0] -= 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if cooldown[0] <= 0:
                if event.key == pygame.K_UP and direction != DOWN and direction != UP:
                    direction = UP; cooldown[0] = cooldown[1]
                elif event.key == pygame.K_DOWN and direction != UP and direction != DOWN:
                    direction = DOWN; cooldown[0] = cooldown[1]
                elif event.key == pygame.K_LEFT and direction != RIGHT and direction != LEFT:
                    direction = LEFT; cooldown[0] = cooldown[1]
                elif event.key == pygame.K_RIGHT and direction != LEFT and direction != RIGHT:
                    direction = RIGHT; cooldown[0] = cooldown[1]
    ate = snake.head.eats(fruit, MOVEMENTS[direction])
    
    snake.move(MOVEMENTS[direction], ate)
    lost = snake.collides()
    won = snake.size_attr == (MAP_SIZE ** 2)
    if ate:
        fruit = (randint(0, MAP_SIZE - 1), randint(0, MAP_SIZE - 1))
        while not snake.is_empty(fruit):
            fruit = (randint(0, MAP_SIZE - 1), randint(0, MAP_SIZE - 1))

    return (fruit, direction, lost, won)

def run():
    snake = SnakeCircularLinkedList()
    lost, won = False, False
    fruit, direction = (randint(0, MAP_SIZE - 1), randint(0, MAP_SIZE - 1)), DOWN
    cooldown = [1, 1]
    while not lost and not won:
        draw_grid()
        fruit, direction, lost, won = update(snake, fruit, direction, cooldown)
        snake.draw()
        pygame.draw.rect(WINDOW, FRUIT_COLOR, (fruit[0] * BLOCK_SIZE, fruit[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        pygame.display.update()
        WINDOW.fill(BG_COLOR)
        CLOCK.tick(12)

    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 32)
    space_font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f"You {'lost' if lost else 'won'}!", True, TEXT_COLOR, None)
    space_text = space_font.render("Press SPACE to close.", True, TEXT_COLOR, None)
    text_rect = text.get_rect()
    space_rect = space_text.get_rect()
    text_rect[0] = WIDTH / 2 - text_rect[2] / 2
    text_rect[1] = HEIGHT / 2 - text_rect[3] / 2
    space_rect[0] = WIDTH / 2 - space_rect[2] / 2
    space_rect[1] = HEIGHT / 2 - space_rect[3] / 2 + text_rect[3]
    running = True
    while running:
        WINDOW.fill(LIGHTER_BG_COLOR)
        WINDOW.blit(text, text_rect)
        WINDOW.blit(space_text, space_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False

        pygame.display.update()

if __name__ == '__main__':
    run()