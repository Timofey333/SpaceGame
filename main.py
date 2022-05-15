import random
import pygame
from pygame import locals
import forward


class Board(pygame.sprite.Group):
    def __init__(self, width_height: tuple[int, int], borders: tuple[int, int], *sprites: list[pygame.sprite.Sprite] | None) -> None:
        self.width = width_height[0]
        self.height = width_height[1]
        self.borders = borders
        self.cell_size = self.height // max(self.borders[0], self.borders[1])
        self.floor_colors = self.generate_floor_colors()
        super().__init__(*sprites)

    def random_cell(self):
        field = [[True for _ in range(self.borders[0])] for _ in range(self.borders[1])]
        for s in self.sprites():
            field[s.y][s.x] = False
        x, y = random.randint(0, self.borders[0] - 1), random.randint(0, self.borders[1] - 1)
        while not field[y][x]:
            x, y = random.randint(0, self.borders[0] - 1), random.randint(0, self.borders[1] - 1)
        Cell(x, y, self)

    def random_cells(self, n: int):
        for _ in range(n):
            self.random_cell()

    def generate_floor_colors(self) -> list[list[str]]:
        floor_colors = []
        for i in range(self.borders[0]):
            m = []
            for j in range(self.borders[1]):
                m.append(random.choice(["#08061b", "#090720"]))
            floor_colors.append(m)
        return floor_colors

    def draw_flor(self, screen: pygame.surface):
        for i in range(self.borders[0]):
            for j in range(self.borders[1]):
                surf = pygame.Surface((self.cell_size, self.cell_size))
                surf.fill(self.floor_colors[i][j])
                screen.blit(surf, (i * self.cell_size, j * self.cell_size))


class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, board: Board) -> None:
        super().__init__(board)
        self.board_x, self.board_y = x, y
        self.board = board
        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("#ffffff")
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.x = x * board.cell_size
        self.rect.y = y * board.cell_size

    def update(self):
        pass

    @property
    def x(self):
        return self.board_x

    @x.setter
    def x(self, new_x):
        self.board_x = new_x
        self.rect.x = self.board_x * board.cell_size

    @property
    def y(self):
        return self.board_y

    @y.setter
    def y(self, new_y):
        self.board_y = new_y
        self.rect.y = self.board_y * board.cell_size

class Player(Cell):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.image = pygame.image.load("Player.png")
        self.image = pygame.transform.scale(self.image,
                                            (self.board.cell_size, self.board.cell_size))
        self.image.set_colorkey("#000000")

    # def update(self, screen: pygame.surface.Surface):
        # collided_sprite = pygame.sprite.spritecollideany()

    def go_forward(self, go_forward):
        forward_x, forward_y = forward.vector(go_forward)
        self.x += forward_x
        self.y += forward_y
        self.image = pygame.transform.rotate(self.image, forward.up_degree(go_forward))

    def up(self):
        self.go_forward(forward.up)

    def down(self):
        self.go_forward(forward.down)

    def right(self):
        self.go_forward(forward.right)

    def left(self):
        self.go_forward(forward.left)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    fps = 30
    screen.fill("#000000")
    board = Board((1000, 1000), (10, 10))

    player = Player(1, 1, board)

    board.random_cells(10)

    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == locals.KEYDOWN:
                d = {locals.K_UP: player.down,
                     locals.K_DOWN: player.up,
                     locals.K_RIGHT: player.right,
                     locals.K_LEFT: player.left}
                if d.get(event.key, None) is not None:
                    d.get(event.key)()
        board.draw_flor(screen)
        board.update()
        board.draw(screen)
        pygame.display.flip()
