import pygame
from pygame import locals

import pyperclip


class InputField(pygame.sprite.Sprite):
    def __init__(self, group, x, y, widht, height, text="",
                 max_simbols=None, passive_color="#ffffff",
                 active_color="#efefef", is_password=False,
                 see_simbols=None):
        super().__init__(group)
        self.width, self.height = widht, height
        self.x, self.y = x, y
        self.text = text
        self.active = False

        self.max_simbols = max_simbols
        self.see_simbols = see_simbols
        self.passive_color, self.active_color = passive_color, active_color
        self.is_password = is_password

        self.update_text()

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.active = True
                    self.update_text()
                    return
            self.update_text()
            self.active = False
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
        if self.active:
            self.image.fill(self.active_color)
        else:
            self.image.fill(self.passive_color)
        text = str(self.text) if not self.is_password else "*" * len(str(self.text))
        if self.see_simbols is not None:
            if len(text) > self.see_simbols:
                text = text[:self.see_simbols - 3] + "..."
        t = pygame.font.SysFont("monospace", int(10 * self.height / 20)).render(text, 1, "#000000")
        self.image.blit(t, (5, 5))
        self.rect = pygame.rect.Rect(self.image.get_rect())
        self.rect.x, self.rect.y = self.x, self.y


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    fps = 30
    screen.fill("#000000")

    g = pygame.sprite.Group()

    field = InputField(g, 10, 10, 500, 100, text="|")

    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            field.event(event)
        g.update()
        g.draw(screen)
        pygame.display.flip()
