import random
import pygame
from pygame import locals
import forward
import particles


class BOardsGroup:
    def __init__(self, *boards):
        self.boards = boards

    def draw(self, screen):
        for board in self.boards:
            board.draw(screen)

    def update(self):
        for board in self.boards:
            board.update()


class Board(pygame.sprite.Group):
    def __init__(self, width_height: tuple[int, int], borders: tuple[int, int],
                 *sprites: list[pygame.sprite.Sprite] or None, fps=30,
                 particle_system: None or particles.ParitcleSystem = None,
                 floor_board=None) -> None:
        self.floor_board = floor_board
        self.width = width_height[0]
        self.height = width_height[1]
        self.borders = borders
        self.cell_size = self.height // max(self.borders[0], self.borders[1])
        self.floor_colors = self.generate_floor_colors()
        self.game_fps = fps
        self.particle_system = particle_system
        super().__init__(*sprites)

    @property
    def ground_board(self):
        return self.floor_board

    @property
    def fps(self) -> int:
        return self.game_fps

    @fps.setter
    def fps(self, n: int):
        self.game_fps = n

    def random_cell(self, cell):
        field = [[True for _ in range(self.borders[0])] for _ in range(self.borders[1])]
        for s in self.sprites():
            field[s.y][s.x] = False
        x, y = random.randint(0, self.borders[0] - 1), random.randint(0, self.borders[1] - 1)
        while not field[y][x]:
            x, y = random.randint(0, self.borders[0] - 1), random.randint(0, self.borders[1] - 1)
        cell(x, y, self, particle_system=self.particle_system)

    def random_cells(self, n: int):
        for _ in range(n):
            self.random_cell(random.choice([Asteroid, Ice, Ice, Ice, IceCrystal]))

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

        self.durability = None
        self.is_concerns = False
        self.is_icing = False

    def update(self):
        self._check_commands()
        self._rotate()
        self._move()
        self.concerns()

    @property
    def cell_durability(self) -> int or None:
        return self.durability

    def knock(self, sprite: pygame.sprite.Sprite, strong=1):
        if self.durability is None:
            self.on_none_knock(sprite)
            return
        self.durability -= strong
        self.on_knock(sprite)
        if self.durability <= 0:
            self.kill()

    def on_knock(self, sprite: pygame.sprite.Sprite):
        pass

    def on_none_knock(self, sprite: pygame.sprite.Sprite):
        pass

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
                self.is_concerns = False
                self.is_icing = False
        if self.progress_y != 100:
            self.progress_y += shift
            if self.progress_y >= 100:
                self.progress_y = 100
                self.now_command = None
                self.is_concerns = False
                self.is_icing = False
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

    def concerns(self, is_place=False):
        if self.board.ground_board is not None:
            m = pygame.sprite.spritecollide(self, self.board.sprites() + self.board.ground_board.sprites(), False)
        else:
            m = pygame.sprite.spritecollide(self, self.board, False)
        for collided_sprite in m:
            if collided_sprite == self:
                continue
            if not (self.board_x == collided_sprite.board_x and self.board_y == collided_sprite.board_y):
                continue
            if collided_sprite is not None:
                concern_cell_types = [Asteroid, Ice, IceCrystal]
                if type(collided_sprite) in concern_cell_types:
                    if self.now_command == self._move_start and (not self.is_concerns):
                        self.is_concerns = True
                        if type(collided_sprite) is Ice:
                            self.commands.insert(0, (
                                self._move_start, forward.opposite(forward.form_up_degree(self.must_forward))))
                            self.is_icing = True
                        if collided_sprite.cell_durability is not None:
                            self.progress_x, self.progress_y = 80, 80
                            i_x, i_y = self.must_x, self.must_y
                            self.must_x, self.must_y = self.start_x, self.start_y
                            self.start_x, self.start_y = i_x, i_y
                            self.board_x, self.board_y = self.last_board_x, self.last_board_y
                            self.now_command = self._move_start
                        if self.is_icing:
                            collided_sprite.knock(self, strong=1000)
                        else:
                            collided_sprite.knock(self)

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


class Asteroid(Cell):
    def __init__(self, x, y, board, particle_system: None or particles.ParitcleSystem = None):
        super().__init__(x, y, board)
        self.particle_system = particle_system
        self.durability = random.randint(1, 6)
        self.start_image = pygame.image.load("Asteroid.png")
        self.start_image = pygame.transform.scale(self.start_image, (self.board.cell_size, self.board.cell_size))
        self.start_image.set_colorkey("#000000")
        self.change_image()
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.board_x * self.board.cell_size, self.board_y * self.board.cell_size

    def change_image(self):
        self.start_image = pygame.image.load("Asteroid.png")
        self.start_image = pygame.transform.scale(self.start_image, (self.board.cell_size, self.board.cell_size))
        self.start_image.set_colorkey("#000000")
        font = pygame.font.SysFont("monospace", self.board.cell_size)
        text = font.render(str(self.durability), 1, "#cecece")
        self.image = self.start_image
        self.image.blit(text, (self.board.cell_size // 5, 0))

    def cnock_particle_anim(self, sprite_must_forward):
        if self.particle_system is None:
            return
        for _ in range(int(20 / self.fps * 30)):
            x_y = (self.place_x + self.board.cell_size // 2, self.place_y + self.board.cell_size // 2)
            d = random.randint(2, 6)
            w_h = (d, d)
            forw = forward.vector(forward.form_up_degree(sprite_must_forward))
            forw = (forw[0] * 8 + random.randint(-40, 40) / 10, forw[1] * 8 + random.randint(-40, 40) / 10)
            l_t = random.randint(10, 20)
            color = "#acacac"
            particles.Particle(self.particle_system,
                               x_y, w_h, forw, l_t, color)

    def on_knock(self, sprite: Cell):
        # TODO: делать нормально!
        self.cnock_particle_anim(sprite.must_forward)
        self.change_image()


class Ice(Cell):
    def __init__(self, x, y, board, particle_system: None or particles.ParitcleSystem = None):
        super().__init__(x, y, board)
        self.particle_system = particle_system
        self.durability = None
        self.image = pygame.image.load("Ice.png")
        self.image = pygame.transform.scale(self.image, (self.board.cell_size, self.board.cell_size))
        self.image.set_colorkey("#000000")
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.board_x * self.board.cell_size, self.board_y * self.board.cell_size

    def cnock_particle_anim(self):
        if self.particle_system is None:
            return
        for _ in range(int(20 / self.fps * 30)):
            x_y = (self.place_x + self.board.cell_size // 2, self.place_y + self.board.cell_size // 2)
            d = random.randint(2, 6)
            w_h = (d, d)
            forw = (random.randint(-50, 50) / 15,
                    random.randint(-50, 50) / 15)
            l_t = random.randint(10, 20)
            color = "#534acb"
            particles.Particle(self.particle_system,
                               x_y, w_h, forw, l_t, color)

    def on_none_knock(self, sprite: Cell):
        self.cnock_particle_anim()


class IceCrystal(Cell):
    def __init__(self, x, y, board, particle_system: None or particles.ParitcleSystem = None):
        super().__init__(x, y, board)
        self.particle_system = particle_system
        self.durability = 1
        self.image = pygame.image.load("IceCrystal.png")
        self.image = pygame.transform.scale(self.image, (self.board.cell_size, self.board.cell_size))
        self.image.set_colorkey("#000000")
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.board_x * self.board.cell_size, self.board_y * self.board.cell_size

    def cnock_particle_anim(self, sprite_must_forward):
        if self.particle_system is None:
            return
        for _ in range(int(20 / self.fps * 30)):
            x_y = (self.place_x + self.board.cell_size // 2, self.place_y + self.board.cell_size // 2)
            d = random.randint(2, 6)
            w_h = (d, d)
            forw = forward.vector(forward.form_up_degree(sprite_must_forward))
            forw = (forw[0] * 8 + random.randint(-40, 40) / 10, forw[1] * 8 + random.randint(-40, 40) / 10)
            l_t = random.randint(10, 20)
            color = "#acacac"
            particles.Particle(self.particle_system,
                               x_y, w_h, forw, l_t, color)

    def on_knock(self, sprite: Cell):
        # TODO: делать нормально!
        self.cnock_particle_anim(sprite.must_forward)
        if self.durability <= 0:
            for x_y in [(0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)]:
                x, y = self.board_x + x_y[0], self.board_y + x_y[1]
                Ice(x, y, self.board.ground_board, self.particle_system)


def random_cells(board, ground, n=10):
    for _ in range(n):
        cell = random.choice([Asteroid, Ice, Ice, Ice, IceCrystal])
        if cell in [Asteroid, IceCrystal]:
            board.random_cell(cell)
        else:
            ground.random_cell(cell)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    fps = 30
    screen.fill("#000000")

    particle_system = particles.ParitcleSystem(fps=fps)

    ground = Board((1000, 1000), (10, 10), fps=fps, particle_system=particle_system)
    board = Board((1000, 1000), (10, 10), fps=fps, particle_system=particle_system, floor_board=ground)

    random_cells(board, ground, n=20)

    player = Player(1, 1, board, particle_system=particle_system)

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
        ground.draw_flor(screen)
        particle_system.update()
        board.update()
        ground.update()
        ground.draw(screen)
        particle_system.draw(screen)
        board.draw(screen)
        pygame.display.flip()
