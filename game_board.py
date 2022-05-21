import random
import pygame
from pygame import locals
import forward
import particles
import item_status
import UITools

OUT_BORDERS_REASON = "Out of borders"


class BoardsGroup:
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
                 floor_board=None, harmless_cells=False) -> None:
        self.floor_board = floor_board
        self.width = width_height[0]
        self.height = width_height[1]
        self._borders = borders
        self._start_borders = borders
        self._left_borders = (-1, -1)
        self.cell_size = self.height // max(self.borders[0], self.borders[1])
        self.floor_colors = self.generate_floor_colors()
        self.game_fps = fps
        self._particle_system = particle_system
        self._destroided_players_id = []
        self.harmless_cells = harmless_cells
        self.zone_cells = []
        if self.floor_board is not None:
            self.zone_event = pygame.event.Event(0)
            self.zone_events_count = 5
            self.randomize_zone_event()
            self.set_cell_event = pygame.event.Event(1)
            pygame.time.set_timer(self.set_cell_event, 10)
            self.random_cell_event = pygame.event.Event(2)
            self.randomize_random_cell_event()
        super().__init__(*sprites)

    @property
    def start_borders(self):
        return self._start_borders

    @property
    def borders(self):
        return self._borders

    @property
    def left_borders(self):
        return self._left_borders

    @property
    def alive_players(self):
        p = []
        for sprite in self.sprites():
            if type(sprite) is Player:
                if sprite.id not in self.destroided_players_id:
                    p.append(sprite)
        return p

    @property
    def destroided_players_id(self):
        return self._destroided_players_id

    @destroided_players_id.setter
    def destroided_players_id(self, n):
        self._destroided_players_id = n

    @property
    def particle_system(self):
        return self._particle_system

    @property
    def ground_board(self):
        return self.floor_board

    @property
    def fps(self) -> int:
        return self.game_fps

    @fps.setter
    def fps(self, n: int):
        self.game_fps = n

    def randomize_zone_event(self):
        pygame.time.set_timer(self.zone_event, random.randint(40, 60) * 1000)

    def randomize_random_cell_event(self):
        pygame.time.set_timer(self.random_cell_event, random.randint(1, 5) * 1000)

    def set_zone_cell(self):
        if len(self.zone_cells) != 0:
            c = self.zone_cells.pop(0)
            ZoneCell(c[0], c[1], self)

    def event(self, event, no_zone=False):
        if self.floor_board is None:
            return
        if event == self.zone_event and not no_zone:
            self.zone()
        elif event == self.set_cell_event:
            self.set_zone_cell()
        elif event == self.random_cell_event:
            random_cells(self, self.floor_board, 1, harmless=self.harmless_cells)

    def zone(self):
        self.zone_events_count -= 1
        if self.zone_events_count <= 0:
            return
        self._borders = (self._borders[0] - 1, self._borders[1] - 1)
        self._left_borders = (self._left_borders[0] + 1, self._left_borders[1] + 1)
        m = self.get_zone_cells_cords()
        random.shuffle(m)
        self.zone_cells += m
        pygame.time.set_timer(self.zone_event, random.randint(40, 60) * 1000)

    def get_zone_cells_cords(self):
        c = []
        for x in range(self.start_borders[0]):
            for y in range(self.start_borders[1]):
                if x == self.left_borders[0] or x == self.borders[0] or \
                        y == self.left_borders[1] or y == self.borders[1]:
                    c.append((x, y))
        return c

    def spawn_players(self, players: list):
        for p in players:
            Player(p.id, None, None, self, particle_system=self.particle_system, name=p.name)

    def in_borders(self, x: int, y: int) -> bool:
        if x < 0 or y < 0:
            return False
        if x >= self.borders[0] or y >= self.borders[1]:
            return False
        return True

    def random_antnes_pos(self):
        field = [[True for _ in range(self.borders[0])] for _ in range(self.borders[1])]
        for s in self.sprites():
            if not self.in_borders(s.x, s.y):
                continue
            field[s.y][s.x] = False
        x, y = random.randint(0, self.borders[0] - 1), random.randint(0, self.borders[1] - 1)
        while not field[y][x]:
            x, y = random.randint(0, self.borders[0] - 1), random.randint(0, self.borders[1] - 1)
        return x, y

    def random_cell(self, cell):
        if len(self.sprites()) >= self.borders[0] * self.borders[1]:
            return
        x, y = self.random_antnes_pos()
        if cell == Bullet:
            cell(x, y, self, item_status.active, particle_system=self.particle_system)
            return
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
        if self.floor_board is not None:
            return
        for i in range(self.borders[1]):
            for j in range(self.borders[0]):
                surf = pygame.Surface((self.cell_size, self.cell_size))
                surf.fill(self.floor_colors[i][j])
                screen.blit(surf, (i * self.cell_size, j * self.cell_size))


class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, board: Board) -> None:
        if x is None:
            x = board.random_antnes_pos()[0]
        if y is None:
            y = board.random_antnes_pos()[1]
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

        self.move_speed = 10
        self.rotate_speed = 10

    @property
    def commands_property(self):
        return self.commands

    def check_borders(self):
        if self.board_x < 0 or self.board_x >= self.board.start_borders[0] or \
                self.board_y < 0 or self.board_y >= self.board.start_borders[1]:
            self.destroid(OUT_BORDERS_REASON)

    def destroid(self, reason: str):
        self.kill()

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
            self.check_borders()
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
            shift = self.rotate_speed * 90 / abs(self.start_forward - self.must_forward) / self.fps * 30
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
        shift = self.move_speed / self.fps * 30
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
                concern_cell_types = [Player, Asteroid, Ice, IceCrystal, ZoneCell, Bullet]
                if type(collided_sprite) in concern_cell_types:
                    if self.now_command == self._move_start and (not self.is_concerns):
                        self.is_concerns = True
                        if collided_sprite.cell_durability is None:
                            # НЕТ СТОЛКНОВЕНИЯ
                            if type(collided_sprite) is Ice:
                                self.commands.insert(0, (
                                    self._move_start, forward.opposite(forward.form_up_degree(self.must_forward))))
                            collided_sprite.on_none_knock(self)
                        else:
                            # ТОЛКНОВЕНИЕ
                            if type(collided_sprite) is Player and type(self) is Player:
                                return
                            self.progress_x, self.progress_y = 80, 80
                            i_x, i_y = self.must_x, self.must_y
                            self.must_x, self.must_y = self.start_x, self.start_y
                            self.start_x, self.start_y = i_x, i_y
                            self.board_x, self.board_y = self.last_board_x, self.last_board_y
                            self.now_command = self._move_start
                            if type(self) == Bullet:
                                collided_sprite.knock(self, strong=3)
                                self.destroid("Was bullet")
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


class ZoneCell(Cell):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.durability = None
        self.image = pygame.surface.Surface((self.board.cell_size, self.board.cell_size))
        self.rect = pygame.rect.Rect(self.image.get_rect())
        self.rect.x = x * self.board.cell_size
        self.rect.y = y * self.board.cell_size
        c = pygame.sprite.spritecollide(self, self.board, False)
        if c is None:
            return
        for sprite in c:
            if sprite == self:
                continue
            self.on_none_knock(sprite)

    def update(self):
        pass

    def on_none_knock(self, sprite: Cell):
        sprite.commands_property.insert(0, (sprite.destroid, OUT_BORDERS_REASON))


class Player(Cell):
    def __init__(self, id, x, y, *groups, particle_system: None or particles.ParitcleSystem = None,
                 name="Player", ui_group=None):
        self.is_init = True
        super().__init__(x, y, *groups)
        self.start_image = pygame.image.load("Player.png")
        self.start_image = pygame.transform.scale(self.start_image,
                                                  (self.board.cell_size, self.board.cell_size))
        self.image = self.start_image
        self.image.set_colorkey("#000000")

        self.player_id = id
        self._name = name

        self.particle_system = particle_system
        self.ui_group = ui_group

        self._items = []

        self.spawn_particle_anim()
        self.is_init = False

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, new_items):
        self._items = new_items

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self.player_id

    def draw_nick_name(self):
        items_text = "".join([{Bullet: "¤"}.get(type(i), "?") for i in self.items])
        text_surf = pygame.font.SysFont("monospace", self.board.cell_size // 5).render(self.name[:5] + items_text,
                                                                                       False, "#ffffff")
        with_text_image = pygame.transform.rotate(self.start_image, self.cell_forward)
        with_text_image.blit(text_surf, (5, 5))
        self.image = with_text_image

    def _rotate(self):
        super()._rotate()
        self.draw_nick_name()

    def can_add_item(self) -> bool:
        return len(self.items) >= 3

    def add_item(self, item) -> bool:
        if self.can_add_item():
            return False
        self.items.append(item)
        return True

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

    def destroid(self, reason):
        self.board.destroided_players_id.append(self.id)
        print(f"player destoroided, reason: {reason}")
        if reason == OUT_BORDERS_REASON and self.ui_group is not None:
            print("Ok")
            sx, sy = self.board_x * self.board.cell_size + self.board.cell_size // 5, \
                     self.board_y * self.board.cell_size + self.board.cell_size // 5
            ex, ey = self.last_board_x * self.board.cell_size + self.board.cell_size // 5, \
                     self.last_board_y * self.board.cell_size + self.board.cell_size // 5
            UITools.PopupText(self.ui_group, (sx, ex), (sy, ey), 100, 100, "Good bye", text_color="#ffffff",
                              kill_timer=7)
        super().destroid(reason)

    def update(self):
        if self.is_init:
            return
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
        if self.is_init:
            return
        self.go_forward(forward.up)

    def down(self):
        if self.is_init:
            return
        self.go_forward(forward.down)

    def right(self):
        if self.is_init:
            return
        self.go_forward(forward.right)

    def left(self):
        if self.is_init:
            return
        self.go_forward(forward.left)

    def use(self):
        if self.is_init:
            return
        self.add_command((self._use, None))

    def _use(self, none: None):
        if len(self.items) == 0:
            self.now_command = None
            return
        self.items.pop(0).use(self)
        self.now_command = None


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

    # def on_none_knock(self, sprite: Cell):
    #     self.cnock_particle_anim()


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


class Bullet(Cell):
    def __init__(self, x, y, board, status, particle_system=None):
        super().__init__(x, y, board)
        self.particle_system = particle_system
        self.durability = None
        self.item_image = pygame.image.load("BulletItem.png")
        self.item_image = self.set_rectangule(self.item_image, 10, 10, 80, 80)
        self.item_image = pygame.transform.scale(self.item_image, (self.board.cell_size, self.board.cell_size))
        self.item_image.set_colorkey("#000000")
        self.go_image = pygame.image.load("Bullet.png")
        self.go_image = self.set_rectangule(self.go_image, 40, 30, 20, 30)
        self.go_image = pygame.transform.scale(self.go_image, (self.board.cell_size, self.board.cell_size))
        self.go_image.set_colorkey("#000000")
        self.image = self.item_image
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.board_x * self.board.cell_size, self.board_y * self.board.cell_size

        self.status = status
        self.move_speed = 30

    def bullet_start_anim(self, sprite_must_forward):
        if self.particle_system is None:
            return
        for _ in range(int(30 / self.fps * 30)):
            x_y = (self.place_x + self.board.cell_size // 2, self.place_y + self.board.cell_size // 2)
            d = random.randint(2, 6)
            w_h = (d, d)
            forw = forward.vector(forward.opposite(forward.form_up_degree(sprite_must_forward)))
            forw = (forw[0] * 8 + random.randint(-10, 10) / 5, forw[1] * 8 + random.randint(-10, 10) / 5)
            l_t = random.randint(10, 20)
            color = "#acacac"
            particles.Particle(self.particle_system,
                               x_y, w_h, forw, l_t, color)

    @staticmethod
    def set_rectangule(surface, x, y, width, height):
        surf = pygame.surface.Surface((100, 100))
        surface = pygame.transform.scale(surface, (int(width), int(height)))
        surf.blit(surface, (int(x), int(y)))
        return surf

    def on_none_knock(self, sprite: Cell):
        if type(sprite) is Player:
            if sprite.add_item(self):
                self.destroid("Was added into Player")
            else:
                pass

    def use(self, sprite: Player):
        self.status = item_status.active
        self.add(sprite.board)
        self.x, self.y = sprite.x + forward.vector(forward.opposite(sprite.must_forward))[0], \
                         sprite.y + forward.vector(forward.opposite(sprite.must_forward))[1]
        self.must_forward = sprite.must_forward
        self._move_start(sprite.must_forward)
        self.progress_x, self.progress_y = 70, 70
        self._move()
        self.durability = 3
        self.image = pygame.transform.rotate(self.go_image, sprite.must_forward)
        self.bullet_start_anim(sprite.must_forward)
        for i in range(10):
            self.move(forward.opposite(sprite.must_forward))


def random_cells(board, ground, n=10, harmless=False):
    m = [Asteroid, IceCrystal, Ice] if harmless else [Asteroid, IceCrystal, Ice, Bullet]
    for _ in range(n):
        cell = random.choice(m)
        if cell in [Asteroid, IceCrystal, Bullet]:
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

    ui_group = pygame.sprite.Group()

    player = Player(1, 1, 1, board, particle_system=particle_system, ui_group=ui_group)

    while True:
        clock.tick(fps)
        screen.fill("#000000")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == locals.KEYDOWN:
                d = {locals.K_UP: player.down,
                     locals.K_DOWN: player.up,
                     locals.K_RIGHT: player.right,
                     locals.K_LEFT: player.left,
                     locals.K_0: player.use}
                if d.get(event.key, None) is not None:
                    d.get(event.key)()
            board.event(event)
        ground.draw_flor(screen)
        particle_system.update()
        board.update()
        ground.update()
        ground.draw(screen)
        particle_system.draw(screen)
        board.draw(screen)
        ui_group.update()
        ui_group.draw(screen)
        pygame.display.flip()
