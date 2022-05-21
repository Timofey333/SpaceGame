import pygame
from pygame import locals

import pyperclip

pygame.init()
pygame.font.init()


class UIGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def event(self, event):
        for sprite in self.sprites():
            if hasattr(sprite, "event") and callable(getattr(sprite, "event")):
                sprite.event(event)


class InputField(pygame.sprite.Sprite):
    def __init__(self, group, x, y, widht, height, text="",
                 max_simbols=None, passive_color="#ffffff",
                 active_color="#efefef", is_password=False,
                 see_simbols=None, ampty_text="",
                 ampty_text_color="#c2c2c2"):
        super().__init__(group)
        self.width, self.height = widht, height
        self.x, self.y = x, y
        self.text = text
        self.ampty_text = ampty_text
        self.ampty_text_color = ampty_text_color
        self.active = False

        self.max_simbols = max_simbols
        self.see_simbols = see_simbols
        self.passive_color, self.active_color = passive_color, active_color
        self.is_password = is_password

        self.update_text()

    @property
    def input_text(self) -> str:
        return self.text

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.active = True
                    self.update_text()
                    return
            self.active = False
            self.update_text()
        if event.type == pygame.KEYDOWN:
            if self.active:
                ctrl = event.mod and pygame.KMOD_CTRL
                if event.key == pygame.K_BACKSPACE and ctrl:
                    self.text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_v and ctrl:
                    self.text += pyperclip.paste()
                elif event.key == pygame.K_c and ctrl:
                    pyperclip.copy(self.text)
                else:
                    input_key = event.unicode
                    if self.max_simbols is not None:
                        if len(self.text) + 1 <= self.max_simbols:
                            self.text += input_key
                    else:
                        self.text += input_key
                self.update_text()

    def update_text(self):
        self.image = pygame.surface.Surface((self.width, self.height))
        self.image = pygame.surface.Surface((self.width, self.height))
        if self.active:
            self.image.fill(self.active_color)
        else:
            self.image.fill(self.passive_color)
        text = str(self.text) if not self.is_password else "*" * len(str(self.text))
        color = "#000000"
        if len(text) == 0:
            text = self.ampty_text
            color = self.ampty_text_color
        if self.see_simbols is not None:
            if len(text) > self.see_simbols:
                text = text[:self.see_simbols - 3] + "..."
        t = pygame.font.SysFont("monospace", int(10 * self.height / 20)).render(text, 1, color)
        self.image.blit(t, (5, 5))
        self.rect = pygame.rect.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.x, self.y


class Button(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, x, y,
                 width, height, text, fill_color="#ffffff",
                 font=pygame.font.SysFont("monospace", 15),
                 text_color="#000000", text_x=5, text_y=5):
        super().__init__(group)
        self.sprite_group = group
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.font = font
        self.fill_color = fill_color
        self.text_clor = text_color
        self.text_x, self.text_y = text_x, text_y

        self.image = pygame.surface.Surface((width, height))
        self.image.fill(fill_color)
        text_surf = font.render(text, 1, text_color)
        self.image.blit(text_surf, (text_x, text_y))
        self.rect = pygame.rect.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = x, y

        self.press_funch = self.on_pressed()

    @property
    def press(self):
        return self.press_funch

    @press.setter
    def press(self, n):
        self.press_funch = n

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.press_funch()

    def on_pressed(self):
        pass


class Text(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, x, y,
                 width, height, text, fill_color="#ffffff",
                 font=pygame.font.SysFont("monospace", 15),
                 text_color="#000000", text_x=0, text_y=0,
                 text_step_y=15, colorkey_color="#00ff00"):
        super().__init__(group)
        self.sprite_group = group
        self.x, self.y = x, y
        self.width, self.height = width, height
        self._text = text
        self.font = font
        self.fill_color = fill_color
        self.text_color = text_color
        self.text_x, self.text_y = text_x, text_y
        self.text_step_y = text_step_y
        self.colorkey_color=colorkey_color
        self.update_image()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text
        self.update_image()

    def update(self):
        pass

    def update_image(self):
        y = self.text_y
        all_text_surf = pygame.surface.Surface((int(self.width), int(self.height)))
        all_text_surf.fill(self.colorkey_color)
        for l in self.text.split("\n"):
            text_surf = self.font.render(l, False, self.text_color)
            all_text_surf.blit(text_surf, (self.text_x, y))
            y += self.text_step_y
        self.image = all_text_surf
        self.image.set_colorkey(self.colorkey_color)
        self.rect = pygame.rect.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.x, self.y


class PopupText(Text):
    def __init__(self, group: pygame.sprite.Group, x: tuple[int, int], y: tuple[int, int],
                 width, height, text, fill_color="#ffffff",
                 font=pygame.font.SysFont("monospace", 15),
                 text_color="#000000", text_x=0, text_y=0,
                 text_step_y=15, speed=3, fps=30, colorkey_color="#00ff00",
                 kill_timer: int or None = None):
        self.is_init = True
        super().__init__(group, x[0], y[0], width, height, text, fill_color=fill_color,
                         font=font, text_color=text_color, text_x=text_x, text_y=text_y,
                         text_step_y=text_step_y, colorkey_color=colorkey_color)
        self.progress = 1
        self.start_x, self.start_y = x[0], y[0]
        self.stop_x, self.stop_y = x[1], y[1]

        self.speed = speed
        self.fps = fps
        self.kill_timer = kill_timer
        self.kill_time = 0

        self.update_image()
        self.is_init = False

    def update(self):
        if self.is_init:
            return
        if self.progress < 100:
            self.progress += self.speed * 30 / self.fps
            self.x = int(self.start_x + (self.stop_x - self.start_x) * self.progress / 100)
            self.y = int(self.start_y + (self.stop_y - self.start_y) * self.progress / 100)
            self.update_image()
        elif self.kill_timer is not None:
            self.kill_time += 1 / self.fps
            if self.kill_time >= self.kill_timer:
                self.kill()


if __name__ == "__main__":
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    fps = 30

    g = pygame.sprite.Group()

    text = PopupText(g, (-50, 50), (50, 50), 100, 100, "Hello world\nhello\nworld", text_color="#000000")

    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        screen.fill("#ffffff")
        g.update()
        g.draw(screen)
        pygame.display.flip()
