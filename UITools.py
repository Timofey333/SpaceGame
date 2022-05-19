import pygame
from pygame import locals

import pyperclip


if __name__ == "__main__":
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
                if event.key == pygame.K_BACKSPACE:
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
                 text_step_y=15):
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
        for l in self.text.split("\n"):
            text_surf = self.font.render(l, 1, self.text_color)
            all_text_surf.blit(text_surf, (self.text_x, y))
            y += self.text_step_y
        self.image = all_text_surf
        self.rect = pygame.rect.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.x, self.y


if __name__ == "__main__":
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    fps = 30
    screen.fill("#000000")

    g = pygame.sprite.Group()

    text = Text(g, 10, 10, 100, 100, "Hello world\nhello\nworld", text_color="#ffffff")

    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        g.update()
        g.draw(screen)
        pygame.display.flip()
