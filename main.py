import random

import pygame
import random


class Board(pygame.sprite.Group):
    def __init__(self, cell_size: int, *sprites: list[pygame.sprite.Sprite] | None) -> None:
        self.cell_size = cell_size
        self.borders = (10, 10)
        self.floor_colors = self.generate_floor_colors()
        super().__init__(*sprites)

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

    def update(self):
        pass

    @property
    def x(self):
        return self.board_x

    @property
    def y(self):
        return self.board_y


class Player(Cell):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.image = pygame.image.load("Player.png")
        self.image = pygame.transform.scale(self.image,
                                            (self.board.cell_size, self.board.cell_size))

    # def update(self, screen: pygame.surface.Surface):
    # collided_sprite = pygame.sprite.spritecollideany()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    fps = 30
    screen.fill("#000000")
    board = Board(50)

    player = Player(0, 0, board)

    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        board.draw_flor(screen)
        board.update()
        board.draw(screen)
        pygame.display.flip()