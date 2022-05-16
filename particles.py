import pygame


class ParitcleSystem(pygame.sprite.Group):
    def __init__(self, fps: int=30):
        super().__init__()
        self.game_fps = fps

    @property
    def fps(self) -> int:
        return self.game_fps

    @fps.setter
    def fps(self, n: int):
        self.game_fps = n


class Particle(pygame.sprite.Sprite):
    def __init__(self, particle_system: pygame.sprite.Group,
                 x_y: tuple[int, int], width_height: tuple[int, int],
                 particle_forward: int,
                 livetime: int, color: str or tuple[int, int, int]):
        super().__init__(particle_system)
        self.particle_system = particle_system
        self.x_y = x_y
        self.widht_height = width_height
        self.particle_forward = particle_forward
        self.livetime = livetime * self.particle_system.fps / 30
        self.color = color
        self.fps = self.particle_system.fps

        self.image = pygame.Surface(self.widht_height)
        self.image.fill(self.color)
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.x_y

    def update(self):
        self.livetime -= 1
        if self.livetime <= 0:
            self.kill()
        x, y = self.x_y
        x = x + self.particle_forward[0] / self.fps * 30
        y = y + self.particle_forward[1] / self.fps * 30
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.x_y = x, y
