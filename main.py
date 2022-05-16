import random
import pygame
from pygame import locals
import forward
import particles


class Board(pygame.sprite.Group):
    def __init__(self, width_height: tuple[int, int], borders: tuple[int, int],
                 *sprites: list[pygame.sprite.Sprite] or None, fps=30) -> None:
        self.width = width_height[0]
        self.height = width_height[1]
        self.borders = borders
        self.cell_size = self.height // max(self.borders[0], self.borders[1])
        self.floor_colors = self.generate_floor_colors()
        self.game_fps = fps
        super().__init__(*sprites)

    @property
    def fps(self) -> int:
        return self.game_fps

    @fps.setter
    def fps(self, n: int):
        self.game_fps = n

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
        self.fps = board.fps

        self.cell_forward = 0
        self.must_forward = 0
        self.place_x = x * board.cell_size
        self.place_y = y * board.cell_size

        self.progress_forward = 100
        self.start_forward = self.cell_forward

        self.start_x = self.place_x
        self.progress_x = 100
        self.start_y = self.place_y
        self.progress_y = 100
        self.must_x = x * board.cell_size
        self.must_y = y * board.cell_size

        self.last_board_x, self.last_board_y = self.board_x, self.board_y

        self.commands = []
        self.now_command = None

    def update(self):
        self._check_commands()
        self._rotate()
        self._move()

    def _check_commands(self):
        if self.now_command is None:
            if len(self.commands) != 0:
                self.perform()

    def _rotate(self):
        if self.progress_forward < 100:
            # подготовительная часть
            s = self.start_forward
            m = self.must_forward
            if s == 0 and m == 270:
                self.start_forward = 360
            if s == 270 and m == 0:
                self.start_forward = -90
        if self.progress_forward < 100:
            # чем больше угол поворота, тем меньше shift
            shift = 900 / abs(self.start_forward - self.must_forward) / self.fps * 30
            # основная часть
            self.progress_forward += shift
            self.cell_forward = int(
                self.start_forward + ((self.must_forward - self.start_forward) * self.progress_forward / 100))
            self.image = pygame.transform.rotate(self.start_image, self.cell_forward)
            if self.progress_forward >= 100:
                self.now_command = None
                self.progress_forward = 100
                self.cell_forward = self.must_forward
                self.image = pygame.transform.rotate(self.start_image, self.cell_forward)

    def _move(self):
        shift = 10 / self.fps * 30
        if self.progress_x != 100:
            self.progress_x += shift
            if self.progress_x >= 100:
                self.progress_x = 100
                self.now_command = None
        if self.progress_y != 100:
            self.progress_y += shift
            if self.progress_y >= 100:
                self.progress_y = 100
                self.now_command = None
        self.place_x = int(self.start_x + ((self.must_x - self.start_x) * self.progress_x / 100))
        self.place_y = int(self.start_y + ((self.must_y - self.start_y) * self.progress_y / 100))
        self.rect.x = self.place_x
        self.rect.y = self.place_y

    def perform(self):
        command = self.commands.pop(0)
        self.now_command = command[0]
        command[0](*command[1:])

    def move(self, move_forward):
        self.add_command((self._move_start, move_forward))

    def _move_start(self, move_forward):
        forward_x, forward_y = forward.vector(move_forward)
        self.x += forward_x
        self.y += forward_y

    def rotate(self, new_rotate: int or str or tuple[int, int]):
        self.add_command((self._rotate_start, new_rotate))

    def _rotate_start(self, new_rotate):
        if self.cell_forward == forward.up_degree(new_rotate):
            self.now_command = None
            return
        self.start_forward = self.must_forward
        if type(new_rotate) == int:
            self.must_forward = new_rotate
        elif type(new_rotate) == str:
            self.must_forward = forward.up_degree(new_rotate)
        elif type(new_rotate) == tuple[int, int]:
            self.must_forward = forward.from_vector(new_rotate)
        self.progress_forward = 1

    def concerns(self):
        for collided_sprite in pygame.sprite.spritecollide(self, self.board, False):
            if collided_sprite == self:
                continue
            if collided_sprite is not None:
                if type(collided_sprite) is Cell:
                    if self.now_command == self._move_start:
                        self.progress_x, self.progress_y = 100, 100
                        self.must_x, self.must_y = self.start_x, self.start_y
                        self.board_x, self.board_y = self.last_board_x, self.last_board_y
                        self.now_command = None
                        self._move()

    def add_command(self, command):
        self.commands.append(command)

    @property
    def x(self):
        return self.board_x

    @x.setter
    def x(self, new_x):
        self.start_x = self.board_x * self.board.cell_size
        self.progress_x = 1
        self.last_board_x = self.board_x
        self.board_x = new_x
        self.must_x = self.board_x * self.board.cell_size

    @property
    def y(self):
        return self.board_y

    @y.setter
    def y(self, new_y):
        self.start_y = self.board_y * self.board.cell_size
        self.progress_y = 1
        self.last_board_y = self.board_y
        self.board_y = new_y
        self.must_y = self.board_y * self.board.cell_size


class Player(Cell):
    def __init__(self, x, y, *groups, particle_system: None or particles.ParitcleSystem = None):
        super().__init__(x, y, *groups)
        self.start_image = pygame.image.load("Player.png")
        self.start_image = pygame.transform.scale(self.start_image,
                                                  (self.board.cell_size, self.board.cell_size))
        self.image = self.start_image
        self.image.set_colorkey("#000000")

        self.particle_system = particle_system

        self.spawn_particle_anim()

    def spawn_particle_anim(self):
        if self.particle_system is None:
            return
        for _ in range(50):
            x_y = (self.place_x + self.board.cell_size // 2, self.place_y + self.board.cell_size // 2)
            d = random.randint(2, 6)
            w_h = (d, d)
            forw = (random.randint(-50, 50) / 15,
                    random.randint(-50, 50) / 15)
            l_t = random.randint(50, 100)
            color = "#ffffff"
            particles.Particle(self.particle_system,
                               x_y, w_h, forw, l_t, color)

    def update(self):
        super().update()
        self.concerns()

    def go_forward(self, go_forward):
        self.rotate(forward.opposite(go_forward))
        self.move(go_forward)

    def create_move_particles(self):
        if self.particle_system is None:
            return
        for _ in range(int(3 / self.fps * 30)):
            x_y = (self.place_x + self.board.cell_size // 2, self.place_y + self.board.cell_size // 2)
            d = random.randint(2, 6)
            w_h = (d, d)
            forw = forward.vector(forward.form_up_degree(self.must_forward))
            forw = (forw[0] * 5 + random.randint(-20, 20) / 10, forw[1] * 5 + random.randint(-20, 20) / 10)
            l_t = random.randint(5, 10)
            color = "#eb1442"
            particles.Particle(self.particle_system,
                               x_y, w_h, forw, l_t, color)

    def _move(self):
        if self.now_command == self._move_start:
            self.create_move_particles()
        super()._move()

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
    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()
    fps = 30
    screen.fill("#000000")
    board = Board((600, 600), (10, 10), fps=fps)

    particle_system = particles.ParitcleSystem(fps=fps)

    player = Player(1, 1, board, particle_system=particle_system)

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
        particle_system.update()
        particle_system.draw(screen)
        board.update()
        board.draw(screen)
        pygame.display.flip()
